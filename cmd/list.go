package cmd

import (
	"encoding/json"
	"fmt"

	"github.com/shalomb/tpcli/pkg/tpclient"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	listWhere  string
	listFields []string
	listTake   int
	listSkip   int
)

var listCmd = &cobra.Command{
	Use:   "list <entity-type>",
	Short: "List entities from TargetProcess",
	Long: `List entities such as UserStories, Bugs, Tasks, Features, etc.

Examples:
  tpcli list UserStories
  tpcli list UserStories --where "EntityState.Name eq 'Open'"
  tpcli list Bugs --fields Id,Name,EntityState --take 10
  tpcli list Tasks --where "Project.Id eq 1234" --take 20`,
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		entityType := args[0]

		// Get configuration - use flags first, then viper fallback
		token, _ := cmd.Flags().GetString("token")
		if token == "" {
			token = viper.GetString("token")
		}

		baseURL, _ := cmd.Flags().GetString("url")
		if baseURL == "" {
			baseURL = viper.GetString("url")
		}

		verboseFlag, _ := cmd.Flags().GetBool("verbose")
		verbose := verboseFlag || viper.GetBool("verbose")

		if token == "" {
			return fmt.Errorf("API token is required (use --token, TP_TOKEN env var, or config file)")
		}
		if baseURL == "" {
			return fmt.Errorf("base URL is required (use --url, TP_URL env var, or config file)")
		}

		// Create client
		client := tpclient.NewClient(baseURL, token, verbose)

		// List entities
		items, err := client.List(entityType, listWhere, listFields, listTake, listSkip)
		if err != nil {
			return fmt.Errorf("listing %s: %w", entityType, err)
		}

		// Output as JSON
		output, err := json.MarshalIndent(items, "", "  ")
		if err != nil {
			return fmt.Errorf("formatting output: %w", err)
		}

		fmt.Println(string(output))
		return nil
	},
}

func init() {
	rootCmd.AddCommand(listCmd)

	listCmd.Flags().StringVar(&listWhere, "where", "", "Filter expression (e.g., 'EntityState.Name eq \"Open\"')")
	listCmd.Flags().StringSliceVar(&listFields, "fields", []string{}, "Fields to include (comma-separated)")
	listCmd.Flags().IntVar(&listTake, "take", 25, "Number of items to retrieve")
	listCmd.Flags().IntVar(&listSkip, "skip", 0, "Number of items to skip")
}
