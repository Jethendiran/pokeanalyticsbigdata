use firestore::{paths, FirestoreCollectionId};
use serde::{Deserialize, Serialize};
use std::fs;
use std::io::Write;

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

    const UPLOAD_LIMIT: usize = 4825;

    let project_root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .ok_or("Project root not found")?
        .to_path_buf();

    let json_path = project_root
        .join("data")
        .join("processed")
        .join("battle_summary.json");

    let error_path = project_root
        .join("data")
        .join("processed")
        .join("upload_failures.csv");

    println!("Reading battle summary JSON...");

    let content = fs::read_to_string(json_path)?;
    let battles: Vec<BattleSummary> = serde_json::from_str(&content)?;

    println!("Total records found: {}", battles.len());

    let db = firestore_connection::connect_firestore().await?;

    let records_to_upload = battles.iter().take(UPLOAD_LIMIT);
    let total = records_to_upload.len();

    let mut uploaded = 0usize;
    let mut failed = 0usize;

    let mut failure_file = fs::File::create(&error_path)?;
    writeln!(failure_file, "episode_id,error")?;

    println!("\nStarting upload of {} records...", total);

    for (index, battle) in records_to_upload.enumerate() {
        let result = db
            .fluent()
            .update()
            .fields(paths!(BattleSummary::{
                episode_id,
                agent_0_reward,
                agent_0_status,
                agent_1_reward,
                agent_1_status,
                battle_outcome,
                total_steps,
                total_events
            }))
            .in_col(COLLECTION)
            .document_id(&battle.episode_id)
            .object(battle)
            .execute::<BattleSummary>()
            .await;

        match result {
            Ok(saved) => {
                uploaded += 1;

                println!(
                    "Uploaded {}/{}: {} ({})",
                    index + 1,
                    total,
                    saved.episode_id,
                    saved.battle_outcome
                );
            }
            Err(error) => {
                failed += 1;

                let safe_error = error.to_string().replace(',', ";");

                writeln!(
                    failure_file,
                    "\"{}\",\"{}\"",
                    battle.episode_id,
                    safe_error
                )?;

                println!(
                    "FAILED {}/{}: {}",
                    index + 1,
                    total,
                    battle.episode_id
                );
                eprintln!("Reason: {}", error);
            }
        }
    }

    println!("\n========== UPLOAD REPORT ==========");
    println!("Records in dataset : {}", battles.len());
    println!("Records attempted  : {}", total);
    println!("Uploaded/updated   : {}", uploaded);
    println!("Failed             : {}", failed);
    println!("Failure log        : {}", error_path.display());

    Ok(())
}

