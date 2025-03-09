# Load libraries
suppressMessages(library(lme4))
suppressMessages(library(lmerTest))
suppressMessages(library(progress))
source("utils.R")

# Define parameters
n_subjects_range <- seq(10, 100, by = 10)  # Adjust as needed
n_iter <- 100
desired_power <- 0.8
p_threshold <- 0.05

# Initialize progress bar
pb <- progress_bar$new(
  format = "Power: :power Iteration: :iteration # Winners: :winners # Losers: :losers",
  total = length(n_subjects_range) * n_iter,
  clear = FALSE,
  width = 60
)

# config
n_iter <- 1000
p_threshold <- 0.05
desired_power <- 0.8
iter <- 1000
tags <- c("10_2.csv", "15_3.csv", "20_4.csv", "25_5.csv", "30_6.csv")
results <- list()

for (t in 1:length(tags)){

# load data
df <- read.csv(paste0("data_", tags[t]))

for (j in seq_along(n_subjects_range)) {
  n_subjects <- n_subjects_range[j]  # Get current N subjects
  success <- c()
  power <- 0
  
  for (i in 1:n_iter) {
    
    # Sample data for this iteration
    sampled_df <- sample_data(df, n_subjects)
    
    # Run the model and determine the winner
    winner <- run_model(sampled_df, p_threshold)
    success <- c(success, ifelse(winner == "Shared", 1, 0))
    
    # Calculate current power
    power <- sum(success) / n_iter
    
    # Update progress bar
    pb$tick(tokens = list(
      power = round(power, 3), 
      iteration = i, 
      winners = sum(success), 
      losers = sum(success == 0)
    ))
    
    # Check power / stopping criteria
    if (sum(success) < (desired_power * i)) {
      break
    } else if (power >= desired_power) {
      results[[j]] <- power
      pb$tick(tokens = list(
        power = round(power, 3), 
        Status = "Stopping early"
      ))
      break
    }
  }
  
  if (power >= desired_power) {
    break
  }
}
}
# aggregate results
results_df <- data.frame(
  n_subjects = n_subjects_range[seq_along(results)],
  achieved_power = unlist(results)
)

# min number of subjects needed
min_subjects_needed <- results_df$n_subjects[which.max(results_df$achieved_power >= desired_power)]

# Print summary results
print(results_df)
cat(sprintf("\nMinimum subjects needed to reach %.2f power: %d\n", desired_power, min_subjects_needed))
