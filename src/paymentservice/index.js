// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0
const grpc = require('@grpc/grpc-js')
const protoLoader = require('@grpc/proto-loader')
const health = require('grpc-js-health-check')
const opentelemetry = require('@opentelemetry/api')

const { context, trace } = require('@opentelemetry/api');
const winston = require('winston');

const { OpenTelemetryTransportV3 } = require('@opentelemetry/winston-transport');
const charge = require('./charge')
const logger = winston.createLogger({
  level: 'info',  
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ timestamp, level, message, ...meta }) => {
    const span = trace.getSpan(context.active());
    const traceId = span ? span.spanContext().traceId : 'N/A';
    const spanId = span ? span.spanContext().spanId : 'N/A';
    return `${timestamp} [${level}] trace_id=${traceId} service.name="paymentservice" span_id=${spanId} body=${JSON.stringify(message)}`;
  })
),
  transports: [
    new winston.transports.Console(),
    new OpenTelemetryTransportV3()
  ]
});

async function chargeServiceHandler(call, callback) {
  const span = opentelemetry.trace.getActiveSpan();

  try {
    const amount = call.request.amount
    span.setAttributes({
      'app.payment.amount': parseFloat(`${amount.units}.${amount.nanos}`)
    })
    logger.info({ request: call.request }, "Charge request received.")

    const response = await charge.charge(call.request)
    callback(null, response)

  } catch (err) {
    logger.warn({ err })

    span.recordException(err)
    span.setStatus({ code: opentelemetry.SpanStatusCode.ERROR })

    callback(err)
  }
}

async function closeGracefully(signal) {
  server.forceShutdown()
  process.kill(process.pid, signal)
}

const otelDemoPackage = grpc.loadPackageDefinition(protoLoader.loadSync('demo.proto'))
const server = new grpc.Server()

server.addService(health.service, new health.Implementation({
  '': health.servingStatus.SERVING
}))

server.addService(otelDemoPackage.oteldemo.PaymentService.service, { charge: chargeServiceHandler })

server.bindAsync(`0.0.0.0:${process.env['PAYMENT_SERVICE_PORT']}`, grpc.ServerCredentials.createInsecure(), (err, port) => {
  if (err) {
    return logger.error({ err })
  }

  logger.info(`PaymentService gRPC server started on port ${port}`)
  server.start()
}
)

process.once('SIGINT', closeGracefully)
process.once('SIGTERM', closeGracefully)
