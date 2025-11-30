package cmd

import (
	"encoding/json"
	"fmt"

	"github.com/shalomb/tpcli/pkg/tpclient"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var planCmd = &cobra.Command{
	Use:   "plan",
	Short: "Manage PI plans (create, update, pull, push)",
	Long: `Manage PI plans in TargetProcess. Future commands will support plan pull and push workflows.

Examples:
  tpcli plan create TeamPIObjective --data '{"name":"Q1 Planning","team_id":1935991,...}'
  tpcli plan update TeamPIObjective 12345 --data '{"effort":40}'`,
}

var createCmd = &cobra.Command{
	Use:   "create <entity-type>",
	Short: "Create a new entity in TargetProcess",
	Long: `Create a new entity in TargetProcess with JSON data.

Examples:
  tpcli plan create TeamPIObjective --data '{"name":"API Perf","team_id":1935991,"release_id":1942235,"effort":34}'
  tpcli plan create Feature --data '{"name":"User Auth","parent_id":2018883,"effort":21}'`,
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		entityType := args[0]
		data, _ := cmd.Flags().GetString("data")

		if data == "" {
			return fmt.Errorf("--data flag is required")
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

		// Create entity
		result, err := client.Create(entityType, []byte(data))
		if err != nil {
			return fmt.Errorf("creating %s: %w", entityType, err)
		}

		// Output as formatted JSON
		var entity map[string]interface{}
		if err := json.Unmarshal(result, &entity); err != nil {
			return fmt.Errorf("parsing response: %w", err)
		}

		output, err := json.MarshalIndent(entity, "", "  ")
		if err != nil {
			return fmt.Errorf("formatting output: %w", err)
		}

		fmt.Println(string(output))
		return nil
	},
}

var updateCmd = &cobra.Command{
	Use:   "update <entity-type> <id>",
	Short: "Update an existing entity in TargetProcess",
	Long: `Update an existing entity in TargetProcess with JSON data.

Examples:
  tpcli plan update TeamPIObjective 12345 --data '{"effort":40}'
  tpcli plan update Feature 5678 --data '{"name":"New Name","effort":13}'`,
	Args: cobra.ExactArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		entityType := args[0]
		id := args[1]
		data, _ := cmd.Flags().GetString("data")

		if data == "" {
			return fmt.Errorf("--data flag is required")
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

		// Update entity
		result, err := client.Update(entityType, id, []byte(data))
		if err != nil {
			return fmt.Errorf("updating %s %s: %w", entityType, id, err)
		}

		// Output as formatted JSON
		var entity map[string]interface{}
		if err := json.Unmarshal(result, &entity); err != nil {
			return fmt.Errorf("parsing response: %w", err)
		}

		output, err := json.MarshalIndent(entity, "", "  ")
		if err != nil {
			return fmt.Errorf("formatting output: %w", err)
		}

		fmt.Println(string(output))
		return nil
	},
}

func init() {
	rootCmd.AddCommand(planCmd)

	planCmd.AddCommand(createCmd)
	createCmd.Flags().String("data", "", "JSON data for entity (required)")

	planCmd.AddCommand(updateCmd)
	updateCmd.Flags().String("data", "", "JSON data for entity (required)")
}
