use axum::extract::State;
use axum::http::StatusCode;
use axum::Json;
use serde_json::Value;

use crate::state::{AppState, Deployment};

pub async fn handle(State(state): State<AppState>, Json(payload): Json<Value>) -> StatusCode {
    println!("got a push");
    let next = Deployment {
        commit: "local".into(),
        branch: "main".into(),
        image_tag: "sagenest-local:dev".into(),
        container_id: "local".into(),
        url: "http://site.localhost/".into(),
    };
    state.swap(next);
    StatusCode::OK
}
