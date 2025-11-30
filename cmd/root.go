package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	cfgFile string
	verbose bool
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
	// 12-factor app precedence:
	// 1. Environment variables (TP_URL, TP_TOKEN) - highest priority
	// 2. Local config file (.tpcli.yaml in current directory)
	// 3. Global config file (~/.config/tpcli/config.yml)
	// 4. Legacy home config (~/.tpcli.yaml) for backwards compatibility
	// 5. Error if none found

	// Bind environment variables first (highest priority)
	viper.SetEnvPrefix("TP")
	viper.AutomaticEnv()
	viper.BindEnv("token", "TP_TOKEN")
	viper.BindEnv("url", "TP_URL")

	// Get home directory for global config paths
	home, err := os.UserHomeDir()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error getting home directory: %v\n", err)
		os.Exit(1)
	}

	viper.SetConfigType("yaml")

	// If config file explicitly specified via flag, use it
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
		_ = viper.ReadInConfig()
	} else {
		// Try to find config file in order of precedence
		xdgPath := os.ExpandEnv("$XDG_CONFIG_HOME/tpcli/config.yaml")
		configFiles := []string{}
		if xdgPath != "" {
			configFiles = append(configFiles, xdgPath) // XDG standard location (if set)
		}
		// Prefer global user config over local repo config
		configFiles = append(configFiles,
			home+"/.config/tpcli/config.yaml", // Global config (~/.config)
			home+"/.tpcli.yaml",               // Legacy home config
			"./.tpcli.yaml",                   // Local config in current directory (lowest priority)
		)

		// Try each config file in order
		for _, cfgPath := range configFiles {
			if _, err := os.Stat(cfgPath); err == nil {
				viper.SetConfigFile(cfgPath)
				if err := viper.ReadInConfig(); err == nil {
					if verbose {
						fmt.Fprintf(os.Stderr, "Using config file: %s\n", viper.ConfigFileUsed())
					}
					return
				}
			}
		}

		if verbose {
			fmt.Fprintf(os.Stderr, "No config file found, using environment variables or flags\n")
		}
	}
}
