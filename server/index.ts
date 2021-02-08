import { createServer } from "http";
import express from "express";
import websocket from "ws";

const app = express();
const server = createServer(app);
const wss = new websocket.Server({ server });

const broadcast = (ws: websocket, object: object) => {
  wss.clients.forEach((client) => {
    if (client.readyState == websocket.OPEN && client !== ws)
      client.send(JSON.stringify(object));
  });
};

wss.on("connection", (ws) => {
  const client_id = Date.now();
  console.log(`Connencted: ${client_id}`);

  ws.send(
    JSON.stringify({
      status: 200,
      message: "Successfully connected",
    })
  );

  broadcast(ws, {
    status: 1000,
    message: "Connected",
    client_id,
  });

  ws.on("message", (message) => {
    broadcast(ws, {
      status: 1002,
      message,
      client_id,
    });
  });

  ws.on("close", function () {
    console.log(`Closed: ${client_id}`);
    broadcast(ws, {
      status: 1001,
      message: "Conenction closed",
      client_id,
    });
  });
});

server.listen(8080, () => console.log("Listening"));
