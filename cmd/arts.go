package cmd

import (
	"encoding/json"
	"fmt"

	"github.com/shalomb/tpcli/pkg/tpclient"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	artsWhere  string
	artsFields []string
	artsTake   int
	artsSkip   int
)

var artsCmd = &cobra.Command{
	Use:   "arts",
	Short: "List Agile Release Trains (ARTs)",
	Long:  "List Agile Release Trains (ARTs) from TargetProcess",
	Args:  cobra.NoArgs,
	RunE: func(cmd *cobra.Command, args []string) error {
		// Get configuration
		token := viper.GetString("token")
		baseURL := viper.GetString("url")
		verboseVal := viper.GetBool("verbose")

		if token == "" {
			return fmt.Errorf("API token is required (use --token, TP_TOKEN env var, or config file)")
		}
		if baseURL == "" {
			return fmt.Errorf("base URL is required (use --url, TP_URL env var, or config file)")
		}

		client := tpclient.NewClient(baseURL, token, verboseVal)

		items, err := client.List("AgileReleaseTrains", artsWhere, artsFields, artsTake, artsSkip)
		if err != nil {
			return fmt.Errorf("listing ARTs: %w", err)
		}

		output, err := json.MarshalIndent(items, "", "  ")
		if err != nil {
			return fmt.Errorf("formatting output: %w", err)
		}

		fmt.Println(string(output))
		return nil
	},
}

func init() {
	rootCmd.AddCommand(artsCmd)

	artsCmd.Flags().StringVar(&artsWhere, "where", "", "Filter expression")
	artsCmd.Flags().StringSliceVar(&artsFields, "fields", []string{}, "Fields to include (comma-separated)")
	artsCmd.Flags().IntVar(&artsTake, "take", 25, "Number of items to retrieve")
	artsCmd.Flags().IntVar(&artsSkip, "skip", 0, "Number of items to skip")
}
