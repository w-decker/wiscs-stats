# imports
suppressMessages(library(lme4))
suppressMessages(library(psych))
suppressMessages(library(dplyr))
suppressMessages(library(lmerTest))

# load data
df <- as.data.frame(read.csv("../data/simulated_shared.csv"))

# model
shared <- lmer(rt ~ modality + question + (1|subject) + (1|question/item) , data = df, REML = FALSE) # nolint
separate <- lmer(rt ~ modality * question + (1 + question|subject) + (1|question/item), data = df, REML = FALSE) # nolint

# output
writeLines(capture.output(summary(shared)), "shared_model_summary.txt")
writeLines(capture.output(summary(separate)), "separate_model_summary.txt")