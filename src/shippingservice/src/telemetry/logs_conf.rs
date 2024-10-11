// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

// use telemetry::init_logger;
use log::{Level};
use opentelemetry::KeyValue;
use opentelemetry_appender_log::OpenTelemetryLogBridge;
use opentelemetry_sdk::logs::{Config, LoggerProvider};
use opentelemetry_sdk::Resource;


pub fn init_logger() -> Result<(), log::SetLoggerError> {

    // Setup LoggerProvider with a stdout exporter
    let exporter = opentelemetry_stdout::LogExporterBuilder::default().build();
    let logger_provider = LoggerProvider::builder()
        .with_config(
            Config::default().with_resource(Resource::new(vec![KeyValue::new(
                "service.name",
                "shippingservice",
            )])),
        )
        .with_simple_exporter(exporter)
        .build();

    // Setup Log Appender for the log crate.
    let otel_log_appender = OpenTelemetryLogBridge::new(&logger_provider);
    log::set_boxed_logger(Box::new(otel_log_appender)).unwrap();
    log::set_max_level(Level::Trace.to_level_filter());
    Ok(())
    // CombinedLogger::init(vec![
    //     SimpleLogger::new(LevelFilter::Info, Config::default()),
    //     SimpleLogger::new(LevelFilter::Warn, Config::default()),
    //     SimpleLogger::new(LevelFilter::Error, Config::default()),
    // ])
}
