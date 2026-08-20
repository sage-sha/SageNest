use axum::extract::State;
use axum::Json;

use crate::state::{AppState, Deployment};

pub async fn status(State(state): State<AppState>) -> Json<Option<Deployment>> {
    Json(state.current())
}
