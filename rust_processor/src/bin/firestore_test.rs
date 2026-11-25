#[path = "../firestore_connection.rs"]
mod firestore_connection;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    println!("Connecting to PokéAnalytics Firestore...");

    let _db = firestore_connection::connect_firestore().await?;

    println!("Firestore connection test completed successfully!");

    Ok(())
}
