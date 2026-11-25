use firestore::FirestoreDb;

const PROJECT_ID: &str = "pokeanalytics-bigdata";

pub async fn connect_firestore() -> Result<FirestoreDb, Box<dyn std::error::Error + Send + Sync>> {
    let db = FirestoreDb::new(PROJECT_ID).await?;

    println!("Firestore client initialized. Checking database access...");

    db.ping().await?;

    println!("Successfully verified Firestore database access!");

    Ok(db)
}
