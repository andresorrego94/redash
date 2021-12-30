from flask import current_app
import datetime
import requests
import json
from redash.worker import job, get_job_logger
from redash import models, utils, settings


logger = get_job_logger(__name__)


def notify_subscriptions(alert, new_state):
    host = utils.base_url(alert.query_rel.org)
    for subscription in alert.subscriptions:
        try:
            subscription.notify(
                alert, alert.query_rel, subscription.user, new_state, current_app, host
            )
        except Exception as e:
            logger.exception("Error with processing destination")


def notify_flow_engine(alert):
    try:
        from redash.serializers import serialize_alert
        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'Authorization': "Key {}".format(settings.FLOW_ENGINE_API_KEY)
        }
        serialized_alert = json.dumps(
            serialize_alert(alert, full=True), sort_keys=True, default=str
        )
        response = requests.post(
            url=settings.FLOW_ENGINE_ALERT_NOTIFY_URL,
            data=serialized_alert,
            headers=headers,
            timeout=5.0,
        )
        if response.status_code == 200:
            logger.info("Alert event was sent to the flow_engine service")
        else:
            logger.error("Error %s sending alert to the flow_engine service", response.status_code)
    except Exception as e:
        logger.exception("Exception sending alert to the flow_engine service")


def should_notify(alert, new_state):
    passed_rearm_threshold = False
    if alert.rearm and alert.last_triggered_at:
        passed_rearm_threshold = (
            alert.last_triggered_at + datetime.timedelta(seconds=alert.rearm)
            < utils.utcnow()
        )

    return new_state != alert.state or (
        alert.state == models.Alert.TRIGGERED_STATE and passed_rearm_threshold
    )


@job("default", timeout=300)
def check_alerts_for_query(query_id):
    logger.debug("Checking query %d for alerts", query_id)

    query = models.Query.query.get(query_id)

    for alert in query.alerts:
        logger.info("Checking alert (%d) of query %d.", alert.id, query_id)
        new_state = alert.evaluate()

        if should_notify(alert, new_state):
            logger.info("Alert %d new state: %s", alert.id, new_state)
            old_state = alert.state

            alert.state = new_state
            alert.last_triggered_at = utils.utcnow()
            models.db.session.commit()

            if (
                old_state == models.Alert.UNKNOWN_STATE
                and new_state == models.Alert.OK_STATE
            ):
                logger.debug(
                    "Skipping notification (previous state was unknown and now it's ok)."
                )
                continue

            notify_flow_engine(alert)

            if alert.muted:
                logger.debug("Skipping notification (alert muted).")
                continue

            notify_subscriptions(alert, new_state)
