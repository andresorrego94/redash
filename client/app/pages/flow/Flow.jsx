import React from "react";
import routes from "@/services/routes";
import routeWithUserSession from "@/components/ApplicationArea/routeWithUserSession";


const Flow = () => {
  const apiKey = "AIvm4lLf9e5vI0jDblmZFoe3NC3AqWvxKNkZZpY7";

  return (
    <>
      <div style={{ height: '100%' }}>
        <iframe style={{ width: '100%', height: '100%' }}  src={`http://tablyx-flow-design.s3-website-sa-east-1.amazonaws.com/${apiKey}`} title="Flow Engine Design"></iframe>
      </div>
    </>
  );
}

export default Flow;

routes.register(
  "Flows.New",
  routeWithUserSession({
    path: "/flows",
    title: "New Flow",
    render: _ => <Flow />,
  })
);