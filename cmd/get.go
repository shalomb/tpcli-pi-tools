package cmd

import (
	"encoding/json"
	"fmt"
	"strconv"

	"github.com/shalomb/tpcli/pkg/tpclient"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	getFields []string
)

var getCmd = &cobra.Command{
	Use:   "get <entity-type> <id>",
	Short: "Get a specific entity by ID",
	Long: `Retrieve a single entity from TargetProcess by its ID.

Examples:
  tpcli get UserStory 12345
  tpcli get Bug 67890 --fields Id,Name,Description,EntityState
  tpcli get Task 111 --fields Id,Name,Project,AssignedUser`,
	Args: cobra.ExactArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		entityType := args[0]
		id, err := strconv.Atoi(args[1])
		if err != nil {
			return fmt.Errorf("invalid ID: %s", args[1])
		}

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

		// Get entity
		item, err := client.Get(entityType, id, getFields)
		if err != nil {
			return fmt.Errorf("getting %s %d: %w", entityType, id, err)
		}

		// Output as JSON
		output, err := json.MarshalIndent(item, "", "  ")
		if err != nil {
			return fmt.Errorf("formatting output: %w", err)
		}

		fmt.Println(string(output))
		return nil
	},
}

func init() {
	rootCmd.AddCommand(getCmd)

	getCmd.Flags().StringSliceVar(&getFields, "fields", []string{}, "Fields to include (comma-separated)")
}
