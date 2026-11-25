use firestore::{FirestoreCollectionId, FirestoreDocumentId};
use serde::{Deserialize, Serialize};

#[path = "../firestore_connection.rs"]
mod firestore_connection;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct BattleTest {
    episode_id: String,
    battle_outcome: String,
    agent_0_reward: i64,
    agent_1_reward: i64,
    total_steps: i64,
    total_events: i64,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    println!("Connecting to Firestore...");

    let db = firestore_connection::connect_firestore().await?;

    const COLLECTION: FirestoreCollectionId =
        FirestoreCollectionId::from_static("battles");

    const DOCUMENT_ID: FirestoreDocumentId =
        FirestoreDocumentId::from_static("rust_connection_test_001");

    let battle = BattleTest {
        episode_id: "rust_connection_test_001".to_string(),
        battle_outcome: "AGENT_0_WIN".to_string(),
        agent_0_reward: 1,
        agent_1_reward: -1,
        total_steps: 125,
        total_events: 1527,
    };

    println!("Uploading test battle...");

    let saved: BattleTest = db
        .fluent()
        .insert()
        .into(COLLECTION)
        .document_id(&DOCUMENT_ID)
        .object(&battle)
        .execute()
        .await?;

    println!("Successfully inserted test document!");
    println!("Episode ID: {}", saved.episode_id);
    println!("Outcome: {}", saved.battle_outcome);

    Ok(())
}
