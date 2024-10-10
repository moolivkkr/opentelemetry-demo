// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

use tonic::transport::Server;

use log::*;

use std::env;

mod shipping_service;
use shipping_service::shop::shipping_service_server::ShippingServiceServer;
use shipping_service::ShippingServer;

mod telemetry;
// use telemetry::init_logger;

use telemetry::init_reqwest_tracing;
use telemetry::init_tracer;

use opentelemetry::global;
use opentelemetry::global::{logger_provider, shutdown_logger_provider, shutdown_tracer_provider};
use opentelemetry::logs::LogError;
use opentelemetry::trace::TraceError;
use opentelemetry::{
    metrics,
    trace::{TraceContextExt, Tracer},
    Key, KeyValue,
};
use opentelemetry_appender_log::OpenTelemetryLogBridge;
use opentelemetry_otlp::{ExportConfig, WithExportConfig};
use opentelemetry_sdk::logs::Config;
use opentelemetry_sdk::{metrics::SdkMeterProvider, runtime, trace as sdktrace, Resource};

fn init_logs() -> Result<opentelemetry_sdk::logs::Logger, LogError> {
    let service_name = "shippingservice";
    opentelemetry_otlp::new_pipeline()
        .logging()
        .with_log_config(
            Config::default().with_resource(Resource::new(vec![KeyValue::new(
                opentelemetry_semantic_conventions::resource::SERVICE_NAME,
                service_name,
            )])),
        )
        .with_exporter(
            opentelemetry_otlp::new_exporter()
                .tonic()
                .with_endpoint("http://localhost:4318"),
        )
        .install_batch(runtime::Tokio)
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // let _ = init_logs();
    // let logger_provider = opentelemetry::global::logger_provider();
    let (mut health_reporter, health_service) = tonic_health::server::health_reporter();
    health_reporter
        .set_serving::<ShippingServiceServer<ShippingServer>>()
        .await;

    init_reqwest_tracing(init_tracer()?)?;
    let _ = init_logs();

    // Retrieve the global LoggerProvider.
    let logger_provider = logger_provider();

    // Create a new OpenTelemetryLogBridge using the above LoggerProvider.
    let otel_log_appender = OpenTelemetryLogBridge::new(&logger_provider);
    log::set_boxed_logger(Box::new(otel_log_appender)).unwrap();
    log::set_max_level(Level::Info.to_level_filter());

    info!("OTel pipeline created");
    let port = env::var("SHIPPING_SERVICE_PORT").expect("$SHIPPING_SERVICE_PORT is not set");
    let addr = format!("0.0.0.0:{}", port).parse()?;
    info!("listening on {}", addr);
    let shipper = ShippingServer::default();

    Server::builder()
        .add_service(ShippingServiceServer::new(shipper))
        .add_service(health_service)
        .serve(addr)
        .await?;

    shutdown_logger_provider();
    Ok(())
}
