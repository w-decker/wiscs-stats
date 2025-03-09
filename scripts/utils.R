suppressMessages(library(lme4))

grid <- function(...) {
  # Generate all possible combinations of elements in K arrays
  # @param ... A list of arrays
  # @return A data frame with all possible combinations of elements in K arrays
  args <- list(...)
  expand.grid(args, KEEP.OUT.ATTRS = FALSE, stringsAsFactors = FALSE)
}

run_model <- function(df, p_threshold) {
  # Run the model and compare the shared vs separate model
  # @param df A data frame with the data
  # @param p_threshold The p-value threshold to compare the models

  # factorize + treatment coding
  df$question <- as.factor(df$question)
  df$subject <- as.factor(df$subject)
  df$item <- as.factor(df$item)
  df$modality <- factor(df$modality, levels = c("word", "image"))
  contrasts(df$modality) <- c(-0.5, 0.5)

  #  set reference levels
  df$question <- relevel(df$question, ref = "0")
  df$item <- relevel(df$item, ref = "0")
    
  control <- lmerControl(optimizer = "bobyqa")
  
  shared <- lmer(rt ~ modality + question + 
                   (1 + question + modality | subject) + 
                   (1 + question + modality | item), 
                 data = df, REML = FALSE, control = control)
  
  separate <- lmer(rt ~ modality * question + 
                     (1 + question + modality | subject) + 
                     (1 + question + modality | item), 
                   data = df, REML = FALSE, control = control)
  
  p_value <- anova(shared, separate, test="Chisq")$`Pr(>Chisq)`[2]
  
  return(ifelse(p_value > p_threshold, "Shared", "Separate"))
}

sample_data <- function(df, n_subjects) {
  # Sample a subset of subjects from the data frame
  # @param df A data frame with the data
  # @param n_subjects The number of subjects to sample
  # @return A data frame with the sampled subjects
  sampled_subjects <- sample(unique(df$subject), n_subjects, replace = FALSE)
  sampled_df <- df[df$subject %in% sampled_subjects, ]
  return(sampled_df)
}
