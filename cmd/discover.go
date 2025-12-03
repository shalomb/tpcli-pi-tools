package cmd

import (
	"encoding/json"
	"fmt"

	"github.com/shalomb/tpcli/pkg/tpclient"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var discoverCmd = &cobra.Command{
	Use:   "discover",
	Short: "Discover TargetProcess entity types and structure",
	Long: `Discover available entity types and their properties.
This helps map out the TargetProcess data model for your instance.

This command connects to your TargetProcess instance and shows:
- All available entity types (Projects, Teams, Features, UserStories, Bugs, etc.)
- How many items of each type exist in your instance
- What fields/properties are available for each type
- Sample data from each type

Use this to discover what entity types you can query with 'tpcli list'.

Examples:
  tpcli discover           # Full discovery with sample data
  tpcli discover -v        # Verbose output with additional details

After discovering, use entity types with 'tpcli list':
  tpcli list Features
  tpcli list UserStories --where "EntityState.Name eq 'Open'"`,
	RunE: func(cmd *cobra.Command, args []string) error {
		// Get configuration from viper (bound to flags and env vars)
		token := viper.GetString("token")
		baseURL := viper.GetString("url")
		verboseVal := viper.GetBool("verbose")

		if token == "" {
			return fmt.Errorf("API token is required (use --token, TP_TOKEN env var, or config file)")
		}
		if baseURL == "" {
			return fmt.Errorf("base URL is required (use --url, TP_URL env var, or config file)")
		}

		// Create client
		client := tpclient.NewClient(baseURL, token, verboseVal)

		// Try basic entity introspection
		fmt.Println("Attempting to discover TargetProcess instance...")
		fmt.Println()

		// List of entity types to discover
		entityTypes := []string{
			"Projects",
			"Epics",
			"Features",
			"UserStories",
			"Bugs",
			"Tasks",
			"Iterations",
			"Releases",
			"Teams",
		}

		discovered := make(map[string]interface{})

		for _, entityType := range entityTypes {
			fmt.Printf("Discovering %s...", entityType)

			// Try to fetch just one item to see the structure
			items, err := client.List(entityType, "", []string{}, 1, 0)
			if err != nil {
				fmt.Printf(" ✗ Error: %v\n", err)
				discovered[entityType] = map[string]interface{}{
					"status": "error",
					"error":  err.Error(),
				}
				continue
			}

			if len(items) == 0 {
				fmt.Println(" (empty)")
				discovered[entityType] = map[string]interface{}{
					"status": "ok",
					"count":  0,
					"sample": nil,
				}
				continue
			}

			fmt.Printf(" ✓ Found %d items\n", len(items))

			// Extract field names from first item
			var fields []string
			item := items[0]
			for key := range item {
				fields = append(fields, key)
			}

			discovered[entityType] = map[string]interface{}{
				"status": "ok",
				"count":  len(items),
				"fields": fields,
				"sample": items[0],
			}
		}

		fmt.Println()
		fmt.Println("=== Discovery Results ===")
		fmt.Println()

		output, err := json.MarshalIndent(discovered, "", "  ")
		if err != nil {
			return fmt.Errorf("formatting output: %w", err)
		}

		fmt.Println(string(output))
		return nil
	},
}

func init() {
	rootCmd.AddCommand(discoverCmd)
}
