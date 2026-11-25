use firestore::{paths, FirestoreCollectionId};
use serde::{Deserialize, Serialize};
use std::fs;
use std::io::Write;

#[path = "../firestore_connection.rs"]
mod firestore_connection;

#[derive(Debug, Clone, Deserialize, Serialize)]
struct CardReference {
    id: i64,
    name: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    const COLLECTION: FirestoreCollectionId =
        FirestoreCollectionId::from_static("cards");

    let project_root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .ok_or("Project root not found")?
        .to_path_buf();

    let json_path = project_root
        .join("data")
        .join("processed")
        .join("card_reference.json");

    let error_path = project_root
        .join("data")
        .join("processed")
        .join("card_upload_failures.csv");

    println!("Reading Pokémon card reference JSON...");

    let content = fs::read_to_string(json_path)?;
    let cards: Vec<CardReference> = serde_json::from_str(&content)?;

    println!("Total cards found: {}", cards.len());

    let db = firestore_connection::connect_firestore().await?;

    let mut uploaded = 0usize;
    let mut failed = 0usize;

    let mut failure_file = fs::File::create(&error_path)?;
    writeln!(failure_file, "card_id,error")?;

    println!("\nStarting card upload...");

    for (index, card) in cards.iter().enumerate() {
        let document_id = card.id.to_string();

        let result = db
            .fluent()
            .update()
            .fields(paths!(CardReference::{id, name}))
            .in_col(COLLECTION)
            .document_id(&document_id)
            .object(card)
            .execute::<CardReference>()
            .await;

        match result {
            Ok(saved) => {
                uploaded += 1;

                println!(
                    "Uploaded {}/{}: {} - {}",
                    index + 1,
                    cards.len(),
                    saved.id,
                    saved.name
                );
            }
            Err(error) => {
                failed += 1;

                writeln!(
                    failure_file,
                    "\"{}\",\"{}\"",
                    card.id,
                    error.to_string().replace(',', ";")
                )?;

                eprintln!("Failed to upload card ID {}: {}", card.id, error);
            }
        }
    }

    println!("\n========== CARD UPLOAD REPORT ==========");
    println!("Total cards found : {}", cards.len());
    println!("Uploaded/updated  : {}", uploaded);
    println!("Failed            : {}", failed);
    println!("Failure log       : {}", error_path.display());

    Ok(())
}
