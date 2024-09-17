// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

const opentelemetry = require("@opentelemetry/sdk-node")

const {getNodeAutoInstrumentations} = require("@opentelemetry/auto-instrumentations-node")
const {OTLPTraceExporter} = require('@opentelemetry/exporter-trace-otlp-grpc')
const {OTLPLogExporter} = require('@opentelemetry/exporter-logs-otlp-grpc')
const {OTLPMetricExporter} = require('@opentelemetry/exporter-metrics-otlp-grpc')
const {PeriodicExportingMetricReader} = require('@opentelemetry/sdk-metrics')
const {alibabaCloudEcsDetector} = require('@opentelemetry/resource-detector-alibaba-cloud')
const {awsEc2Detector, awsEksDetector} = require('@opentelemetry/resource-detector-aws')
const {containerDetector} = require('@opentelemetry/resource-detector-container')
const {gcpDetector} = require('@opentelemetry/resource-detector-gcp')
const {Resource, envDetector, hostDetector, osDetector, processDetector} = require('@opentelemetry/resources')
const logsAPI = require('@opentelemetry/api-logs');
const {LoggerProvider, BatchLogRecordProcessor, ConsoleLogRecordExporter} = require('@opentelemetry/sdk-logs');
const {BatchSpanProcessor} = require('@opentelemetry/sdk-trace-base')
const { RuntimeNodeInstrumentation } = require('@opentelemetry/instrumentation-runtime-node');
const {process} = require("process");
const winston = require('winston');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');


const otel_service_name = "paymentservice";
const resource = new Resource({
  ["service.name"]: otel_service_name
});
const { WinstonInstrumentation } = require('@opentelemetry/instrumentation-winston');
const { OpenTelemetryTransportV3 } = require('@opentelemetry/winston-transport');

const loggerProvider = new LoggerProvider();
const logExporter = new OTLPLogExporter();
loggerProvider.addLogRecordProcessor(new BatchLogRecordProcessor(logExporter));
loggerProvider.resource = resource;
logsAPI.logs.setGlobalLoggerProvider(loggerProvider);

const traceExporter = new OTLPTraceExporter();
const spanProcessor = new BatchSpanProcessor(traceExporter)

const sdk = new opentelemetry.NodeSDK({  
  logProvider: loggerProvider,  
  traceExporter:traceExporter ,
  spanProcessor: spanProcessor,
  instrumentations: [
    new WinstonInstrumentation({
      logHook: (span, record) => {
        const spanContext = span.spanContext();
        record['service.name'] = otel_service_name;
        record['serviceName'] = otel_service_name;
        record['trace_id'] = spanContext.traceId;
        record['span_id'] = spanContext.spanId;
        record['trace_flags'] = spanContext.traceFlags;        
      },
   }),
    new RuntimeNodeInstrumentation({
      eventLoopUtilizationMeasurementInterval:5000
    }),
    getNodeAutoInstrumentations({
      // only instrument fs if it is part of another trace
      '@opentelemetry/instrumentation-fs': {
        requireParentSpan: true,
        enabled: false
      },
      '@opentelemetry/instrumentation-http': {
        enabled: true,
        responseHook: (span,info) => {
          span.updateName(`${info.req.method} ${info.req.path || ''}`);
        }
      },  
      autoDetectResources: true     
    })
  ],
  metricReader: new PeriodicExportingMetricReader({
    exporter: new OTLPMetricExporter()
  }),   
   
})

try{
  sdk.start();
  console.info(" initialization completed for opentelemetry SDK")

}
catch(error){
  console.error("Error initializing opentelemetry SDK, no telemetry would be generated", error)
}


// process.on("SIGTERM", () => {
//   sdk
//     .shutdown()
//     .then(
//       () => console.log("SDK shut down successfully"),
//       (err) => console.log("Error shutting down SDK", err)
//     )
//     .finally(() => process.exit(0));
// });