import React from "react";
import routes from "@/services/routes";
import routeWithUserSession from "@/components/ApplicationArea/routeWithUserSession";


const Flow = () => {
  return (
    <>
      <div style={{ height: '100%' }}>
        <iframe style={{ width: '100%', height: '100%' }} src="https://tablyx-flow-designer.web.app/" title="W3Schools Free Online Web Tutorials"></iframe>
        {/* <iframe style={{ width: '100%', height: '100%' }}  src="http://localhost:3000/token-prueba" title="Flow Engine Design"></iframe> */}
        {/* <object style={{ width: '100%', height: '100%' }} type="text/html" data="https://tablyx-flow-designer.web.app/"></object> */}
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