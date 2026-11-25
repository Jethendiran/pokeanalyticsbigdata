use serde_json::{json, Value};
use std::fs;
use std::path::PathBuf;
use walkdir::WalkDir;

fn classify_battle(rewards: &[Value]) -> &'static str {
    if rewards.len() != 2 {
        return "INCOMPLETE";
    }

    match (
        rewards[0].as_i64(),
        rewards[1].as_i64(),
    ) {
        (Some(1), Some(-1)) => "AGENT_0_WIN",
        (Some(-1), Some(1)) => "AGENT_1_WIN",
        (Some(0), Some(0)) => "DRAW",
        _ => "INCOMPLETE",
    }
}

fn csv_value(value: &Value) -> String {
    match value {
        Value::Null => String::new(),
        _ => value.to_string(),
    }
}

fn main() {
    println!("==============================================");
    println!("     POKEANALYTICS - RUST EPISODE PROCESSOR");
    println!("==============================================");

    let project_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("Project root not found")
        .to_path_buf();

    let raw_dir = project_root.join("data").join("raw");
    let output_dir = project_root.join("data").join("processed");

    fs::create_dir_all(&output_dir)
        .expect("Could not create processed directory");

    let mut records: Vec<Value> = Vec::new();
    let mut total_files = 0;
    let mut failed_files = 0;

    let mut agent_0_wins = 0;
    let mut agent_1_wins = 0;
    let mut draws = 0;
    let mut incomplete = 0;
    let mut total_steps = 0;
    let mut total_events = 0;

    println!("Reading: {}", raw_dir.display());

    for entry in WalkDir::new(&raw_dir)
        .into_iter()
        .filter_map(|e| e.ok())
    {
        let path = entry.path();

        if !path.is_file()
            || path.extension().and_then(|e| e.to_str()) != Some("json")
        {
            continue;
        }

        total_files += 1;

        let content = match fs::read_to_string(path) {
            Ok(content) => content,
            Err(_) => {
                failed_files += 1;
                continue;
            }
        };

        let data: Value = match serde_json::from_str(&content) {
            Ok(data) => data,
            Err(_) => {
                failed_files += 1;
                continue;
            }
        };

        let episode_id = data["id"]
            .as_str()
            .unwrap_or("UNKNOWN");

        let rewards = data["rewards"]
            .as_array()
            .cloned()
            .unwrap_or_default();

        let statuses = data["statuses"]
            .as_array()
            .cloned()
            .unwrap_or_default();

        let steps = data["steps"]
            .as_array()
            .cloned()
            .unwrap_or_default();

        let outcome = classify_battle(&rewards);

        match outcome {
            "AGENT_0_WIN" => agent_0_wins += 1,
            "AGENT_1_WIN" => agent_1_wins += 1,
            "DRAW" => draws += 1,
            _ => incomplete += 1,
        }

        let mut event_count = 0;

        for step in &steps {
            if let Some(agents) = step.as_array() {
                for agent in agents {
                    if let Some(logs) =
                        agent["observation"]["logs"].as_array()
                    {
                        event_count += logs.len();
                    }
                }
            }
        }

        total_steps += steps.len();
        total_events += event_count;

        let record = json!({
            "episode_id": episode_id,
            "agent_0_reward": rewards.get(0).cloned().unwrap_or(Value::Null),
            "agent_1_reward": rewards.get(1).cloned().unwrap_or(Value::Null),
            "agent_0_status": statuses.get(0).cloned().unwrap_or(Value::Null),
            "agent_1_status": statuses.get(1).cloned().unwrap_or(Value::Null),
            "battle_outcome": outcome,
            "total_steps": steps.len(),
            "total_events": event_count
        });

        records.push(record);
    }

    // Save JSON output
    let json_path = output_dir.join("battle_summary.json");

    fs::write(
        &json_path,
        serde_json::to_string_pretty(&records)
            .expect("Could not serialize JSON")
    ).expect("Could not write JSON output");

    // Save CSV output
    let csv_path = output_dir.join("battle_summary.csv");

    let mut csv = String::from(
        "episode_id,agent_0_reward,agent_1_reward,agent_0_status,agent_1_status,battle_outcome,total_steps,total_events\n"
    );

    for record in &records {
        let row = vec![
            csv_value(&record["episode_id"]),
            csv_value(&record["agent_0_reward"]),
            csv_value(&record["agent_1_reward"]),
            csv_value(&record["agent_0_status"]),
            csv_value(&record["agent_1_status"]),
            csv_value(&record["battle_outcome"]),
            csv_value(&record["total_steps"]),
            csv_value(&record["total_events"]),
        ];

        csv.push_str(&row.join(","));
        csv.push('\n');
    }

    fs::write(&csv_path, csv)
        .expect("Could not write CSV output");

    println!("\n=============== RESULTS =================");
    println!("Files discovered    : {}", total_files);
    println!("Episodes processed  : {}", records.len());
    println!("Failed files        : {}", failed_files);
    println!("Agent 0 wins        : {}", agent_0_wins);
    println!("Agent 1 wins        : {}", agent_1_wins);
    println!("Draws               : {}", draws);
    println!("Incomplete episodes : {}", incomplete);
    println!("Total battle steps  : {}", total_steps);
    println!("Total battle events : {}", total_events);

    println!("\nOutput files:");
    println!("{}", json_path.display());
    println!("{}", csv_path.display());

    println!("\nRUST PROCESSING COMPLETED!");
}
