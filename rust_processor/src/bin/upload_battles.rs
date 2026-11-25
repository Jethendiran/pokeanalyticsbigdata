use firestore::{FirestoreCollectionId, FirestoreDocumentId};
use serde::{Deserialize, Serialize};
use std::fs;

#[path = "../firestore_connection.rs"]
mod firestore_connection;

#[derive(Debug, Clone, Deserialize, Serialize)]
struct BattleSummary {
    episode_id: String,
    agent_0_reward: Option<i64>,
    agent_0_status: Option<String>,
    agent_1_reward: Option<i64>,
    agent_1_status: Option<String>,
    battle_outcome: String,
    total_steps: usize,
    total_events: usize,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    const COLLECTION: FirestoreCollectionId =
        FirestoreCollectionId::from_static("battles");

    let project_root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .ok_or("Project root not found")?
        .to_path_buf();

    let json_path = project_root
        .join("data")
        .join("processed")
        .join("battle_summary.json");

    println!("Reading battle summary JSON...");

    let content = fs::read_to_string(json_path)?;
    let battles: Vec<BattleSummary> = serde_json::from_str(&content)?;

    println!("Total records found: {}", battles.len());

    let db = firestore_connection::connect_firestore().await?;

    println!("Uploading first 5 test records...");

    for (index, battle) in battles.iter().take(5).enumerate() {
        let document_id =
            FirestoreDocumentId::new(battle.episode_id.clone())?;

        let saved: BattleSummary = db
            .fluent()
            .insert()
            .into(COLLECTION)
            .document_id(&document_id)
            .object(battle)
            .execute()
            .await?;

        println!(
            "Uploaded {}/5: {} ({})",
            index + 1,
            saved.episode_id,
            saved.battle_outcome
        );
    }

    println!("\nTEST UPLOAD COMPLETED!");

    Ok(())
}

