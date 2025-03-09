# Load necessary libraries
suppressMessages(library(lme4))
suppressMessages(library(lmerTest))
suppressMessages(library(progress))
suppressMessages(library(foreach))
suppressMessages(library(doParallel))
source("utils.R")

# Set up parallel backend
num_cores <- detectCores() - 1  # Use all but one core
cl <- makeCluster(num_cores, outfile = "")  # outfile="" sends worker logs to master
clusterEvalQ(cl, {
  library(lme4)
  library(lmerTest)
  library(progress)
  library(foreach)
  library(doParallel)
  source("utils.R")     
})
registerDoParallel(cl)

# Define parameters
n_subjects_range <- seq(100, 500, by = 100)
n_iter <- 100
desired_power <- 0.8
p_threshold <- 0.05

tags <- c("_10_2.csv", "_15_3.csv", "_20_4.csv", "_25_5.csv", "_30_6.csv")

# Function to run power simulation for one dataset
run_simulation <- function(tag) {
  
  # Load data
  df <- read.csv(paste0("data/data", tag))
  
  # store results
  results_list <- list()
  
  for (j in seq_along(n_subjects_range)) {
    n_subjects <- n_subjects_range[j]  # Get current N subjects
    
    # Run iterations in parallel
    success <- foreach(i = 1:n_iter, .combine = c, .packages = c("lme4")) %dopar% {
      sampled_df <- sample_data(df, n_subjects)
      winner <- run_model(sampled_df, p_threshold)
      return(ifelse(winner == "Shared", 1, 0))
    }
    
    # Calculate power
    power <- sum(success) / n_iter
    results_list[[j]] <- power
    
    # Stop early if power is reached
    if (power >= desired_power) break
  }
  
  return(data.frame(n_subjects = n_subjects_range[seq_along(results_list)], achieved_power = unlist(results_list)))
}

# Run simulations in parallel for all datasets
results_list <- foreach(t = 1:length(tags), .combine = rbind, .packages = c("lme4", "lmerTest")) %dopar% {
  run_simulation(tags[t])
}

# Stop the cluster after computations
stopCluster(cl)

# Aggregate results
results_df <- do.call(rbind, results_list)

# Find minimum number of subjects needed
min_subjects_needed <- results_df$n_subjects[which.max(results_df$achieved_power >= desired_power)]

# Print summary results
print(results_df)
cat(sprintf("\nMinimum subjects needed to reach %.2f power: %d\n", desired_power, min_subjects_needed))