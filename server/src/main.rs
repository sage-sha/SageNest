mod api;
mod builder;
mod runner;
mod state;
mod webhook;

use axum::routing::{get, post};
use axum::Router;
use state::AppState;

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let state = AppState::default();

    let app = Router::new()
        .route("/health", get(|| async { "ok" }))
        .route("/webhook", post(webhook::handle))
        .route("/api/status", get(api::status))
        .with_state(state);

    tracing::info!("http://localhost:3000");
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000")
        .await
        .expect("couldn't bind port 3000");
    axum::serve(listener, app).await.unwrap();
}
