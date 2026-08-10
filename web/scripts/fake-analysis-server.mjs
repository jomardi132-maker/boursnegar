import http from "node:http";

const port = Number(process.env.FAKE_ANALYSIS_PORT || 3394);
const payload = JSON.stringify({
  live_price: { last_price: 1000, pe_ratio: 8 },
  report_used: { tracing_no: "TEST-TRACE-1" },
});

http
  .createServer((_request, response) => {
    response.writeHead(200, { "content-type": "application/json" });
    response.end(payload);
  })
  .listen(port, "127.0.0.1", () => console.log("FAKE_ANALYSIS_READY"));
