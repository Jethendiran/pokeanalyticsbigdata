use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Debug, Deserialize)]
struct BattleSummary {
    episode_id: String,
    battle_outcome: String,
    total_steps: usize,
    total_events: usize,
}

#[derive(Debug, Serialize)]
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

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let project_root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .ok_or("Project root not found")?
        .to_path_buf();

    let input_path = project_root
        .join("data")
        .join("processed")
        .join("battle_summary.json");

    let output_path = project_root
        .join("data")
        .join("analytics")
        .join("analytics_summary.json");

    println!("Reading processed battle data...");

    let content = fs::read_to_string(input_path)?;
    let battles: Vec<BattleSummary> = serde_json::from_str(&content)?;

    let total_battles = battles.len();

    let mut agent_0_wins = 0usize;
    let mut agent_1_wins = 0usize;
    let mut draws = 0usize;
    let mut incomplete_battles = 0usize;
    let mut total_steps = 0usize;
    let mut total_events = 0usize;

    for battle in &battles {
        match battle.battle_outcome.as_str() {
            "AGENT_0_WIN" => agent_0_wins += 1,
            "AGENT_1_WIN" => agent_1_wins += 1,
            "DRAW" => draws += 1,
            "INCOMPLETE" => incomplete_battles += 1,
            other => {
                eprintln!(
                    "Unknown outcome '{}' for episode {}",
                    other, battle.episode_id
                );
            }
        }

        total_steps += battle.total_steps;
        total_events += battle.total_events;
    }

    let decisive_battles = agent_0_wins + agent_1_wins;

    let agent_0_win_rate = if decisive_battles > 0 {
        agent_0_wins as f64 / decisive_battles as f64 * 100.0
    } else {
        0.0
    };

    let agent_1_win_rate = if decisive_battles > 0 {
        agent_1_wins as f64 / decisive_battles as f64 * 100.0
    } else {
        0.0
    };

    let average_steps_per_battle = if total_battles > 0 {
        total_steps as f64 / total_battles as f64
    } else {
        0.0
    };

    let average_events_per_battle = if total_battles > 0 {
        total_events as f64 / total_battles as f64
    } else {
        0.0
    };

    let analytics = AnalyticsSummary {
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
        average_events_per_battle,
    };

    fs::create_dir_all(output_path.parent().unwrap())?;

    let json_output = serde_json::to_string_pretty(&analytics)?;
    fs::write(&output_path, json_output)?;

    println!("\n========== POKEANALYTICS REPORT ==========");
    println!("Total battles       : {}", total_battles);
    println!("Agent 0 wins        : {}", agent_0_wins);
    println!("Agent 1 wins        : {}", agent_1_wins);
    println!("Draws               : {}", draws);
    println!("Incomplete battles  : {}", incomplete_battles);
    println!("Decisive battles    : {}", decisive_battles);
    println!("Agent 0 win rate    : {:.2}%", agent_0_win_rate);
    println!("Agent 1 win rate    : {:.2}%", agent_1_win_rate);
    println!("Total battle steps  : {}", total_steps);
    println!("Total battle events : {}", total_events);
    println!("Average steps       : {:.2}", average_steps_per_battle);
    println!("Average events      : {:.2}", average_events_per_battle);

    println!("\nAnalytics saved to: {}", output_path.display());
    println!("RUST ANALYTICS COMPLETED!");

    Ok(())
}
