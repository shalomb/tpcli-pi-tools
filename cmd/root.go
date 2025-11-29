package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	cfgFile  string
	verbose  bool
)

var rootCmd = &cobra.Command{
	Use:   "tpcli",
	Short: "TargetProcess CLI - A command-line interface for TargetProcess/Apptio",
	Long: `tpcli is a CLI tool for interacting with the TargetProcess REST API.
It supports querying user stories, bugs, tasks, and other entities,
as well as creating and updating items.`,
}

// Execute runs the root command
func Execute() error {
	return rootCmd.Execute()
}

func init() {
	cobra.OnInitialize(initConfig)

	// Global flags
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.tpcli.yaml)")
	rootCmd.PersistentFlags().String("token", "", "TargetProcess API token")
	rootCmd.PersistentFlags().String("url", "", "TargetProcess base URL (e.g., https://company.tpondemand.com)")
	rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "verbose output")

	// Bind flags to viper
	viper.BindPFlag("token", rootCmd.PersistentFlags().Lookup("token"))
	viper.BindPFlag("url", rootCmd.PersistentFlags().Lookup("url"))
	viper.BindPFlag("verbose", rootCmd.PersistentFlags().Lookup("verbose"))
}

func initConfig() {
	// Read from environment variables with TP_ prefix first
	viper.SetEnvPrefix("TP")
	viper.AutomaticEnv()

	// Bind specific env vars
	viper.BindEnv("token", "TP_TOKEN")
	viper.BindEnv("url", "TP_URL")

	// Load config file if specified or exists
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	} else {
		home, err := os.UserHomeDir()
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error getting home directory: %v\n", err)
			os.Exit(1)
		}

		viper.AddConfigPath(home)
		viper.SetConfigType("yaml")
		viper.SetConfigName(".tpcli")
	}

	// Read config file if it exists
	if err := viper.ReadInConfig(); err == nil && verbose {
		fmt.Fprintf(os.Stderr, "Using config file: %s\n", viper.ConfigFileUsed())
	}
}
