use firestore::{paths, FirestoreCollectionId};
use serde::{Deserialize, Serialize};
use std::fs;

#[path = "../firestore_connection.rs"]
mod firestore_connection;

#[derive(Debug, Clone, Deserialize, Serialize)]
struct AnalyticsSummary {
    total_battles: usize,
    agent_0_wins: usize,
    agent_1_wins: usize,
    draws: usize,
    incomplete_battles: usize,
    decisive_battles: usize,
    agent_0_win_rate: f64,
    agent_1_win_rate: f64,
    total_steps: usize,
    total_events: usize,
    average_steps_per_battle: f64,
    average_events_per_battle: f64,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    const COLLECTION: FirestoreCollectionId =
        FirestoreCollectionId::from_static("analytics");

    let project_root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .ok_or("Project root not found")?
        .to_path_buf();

    let json_path = project_root
        .join("data")
        .join("analytics")
        .join("analytics_summary.json");

    println!("Reading analytics summary...");

    let content = fs::read_to_string(json_path)?;
    let analytics: AnalyticsSummary = serde_json::from_str(&content)?;

    let db = firestore_connection::connect_firestore().await?;

    println!("Uploading analytics to Firestore...");

    let saved: AnalyticsSummary = db
        .fluent()
        .update()
        .fields(paths!(AnalyticsSummary::{
            total_battles,
            agent_0_wins,
            agent_1_wins,
            draws,
            incomplete_battles,
            decisive_battles,
            agent_0_win_rate,
            agent_1_win_rate,
            total_steps,
            total_events,
            average_steps_per_battle,
            average_events_per_battle
        }))
        .in_col(COLLECTION)
        .document_id("overall_summary")
        .object(&analytics)
        .execute()
        .await?;

    println!("\n========== FIRESTORE ANALYTICS ==========");
    println!("Document ID       : overall_summary");
    println!("Total battles     : {}", saved.total_battles);
    println!("Agent 0 win rate  : {:.2}%", saved.agent_0_win_rate);
    println!("Agent 1 win rate  : {:.2}%", saved.agent_1_win_rate);
    println!("Total events      : {}", saved.total_events);
    println!("ANALYTICS UPLOAD COMPLETED!");

    Ok(())
}
