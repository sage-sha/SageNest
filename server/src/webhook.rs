use axum::extract::State;
use axum::http::StatusCode;
use axum::Json;
use serde_json::Value;

use crate::state::AppState;

pub async fn handle(State(state): State<AppState>, Json(payload): Json<Value>) -> StatusCode {
    todo!()
}
