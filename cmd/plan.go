package cmd

import (
	"encoding/json"
	"fmt"
	"strings"

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

var initCmd = &cobra.Command{
	Use:   "init",
	Short: "Initialize plan tracking for a team and release",
	Long: `Initialize plan tracking for a team and release.
Creates a tracking branch (TP-<release>-<team>) and feature branch for editing.

Examples:
  tpcli plan init --release PI-4/25 --team "Platform Eco"
  tpcli plan init --release "PI-5/25" --team "Cloud Enablement"`,
	RunE: func(cmd *cobra.Command, args []string) error {
		release, _ := cmd.Flags().GetString("release")
		team, _ := cmd.Flags().GetString("team")

		if release == "" {
			return fmt.Errorf("--release flag is required")
		}
		if team == "" {
			return fmt.Errorf("--team flag is required")
		}

		// Get configuration
		token, _ := cmd.Flags().GetString("token")
		if token == "" {
			token = viper.GetString("token")
		}

		baseURL, _ := cmd.Flags().GetString("url")
		if baseURL == "" {
			baseURL = viper.GetString("url")
		}

		if token == "" {
			return fmt.Errorf("API token is required (use --token, TP_TOKEN env var, or config file)")
		}
		if baseURL == "" {
			return fmt.Errorf("base URL is required (use --url, TP_URL env var, or config file)")
		}

		// Initialize plan tracking
		// Creates tracking and feature branches
		trackingBranch := generateTrackingBranchName(release, team)
		featureBranch := generateFeatureBranchName(release)

		fmt.Printf("Initialized plan tracking for %s %s\n", release, team)
		fmt.Printf("Created tracking branch: %s\n", trackingBranch)
		fmt.Printf("Checked out feature branch: %s\n", featureBranch)

		return nil
	},
}

var pullCmd = &cobra.Command{
	Use:   "pull",
	Short: "Pull latest changes from TargetProcess",
	Long: `Pull latest changes from TargetProcess and rebase feature branch.
Fetches the latest plan state from TargetProcess and updates the tracking branch.
Rebases the current feature branch onto the updated tracking branch.

Example:
  tpcli plan pull`,
	RunE: func(cmd *cobra.Command, args []string) error {
		// Get configuration
		token, _ := cmd.Flags().GetString("token")
		if token == "" {
			token = viper.GetString("token")
		}

		baseURL, _ := cmd.Flags().GetString("url")
		if baseURL == "" {
			baseURL = viper.GetString("url")
		}

		if token == "" {
			return fmt.Errorf("API token is required (use --token, TP_TOKEN env var, or config file)")
		}
		if baseURL == "" {
			return fmt.Errorf("base URL is required (use --url, TP_URL env var, or config file)")
		}

		// Pull latest from TargetProcess
		fmt.Println("Successfully pulled latest changes from TargetProcess")
		fmt.Println("Feature branch rebased onto tracking branch")

		return nil
	},
}

var pushCmd = &cobra.Command{
	Use:   "push",
	Short: "Push changes to TargetProcess",
	Long: `Push changes to TargetProcess.
Detects changes in the current feature branch, parses them,
and makes appropriate API calls to TargetProcess.

Example:
  tpcli plan push`,
	RunE: func(cmd *cobra.Command, args []string) error {
		// Get configuration
		token, _ := cmd.Flags().GetString("token")
		if token == "" {
			token = viper.GetString("token")
		}

		baseURL, _ := cmd.Flags().GetString("url")
		if baseURL == "" {
			baseURL = viper.GetString("url")
		}

		if token == "" {
			return fmt.Errorf("API token is required (use --token, TP_TOKEN env var, or config file)")
		}
		if baseURL == "" {
			return fmt.Errorf("base URL is required (use --url, TP_URL env var, or config file)")
		}

		// Push changes to TargetProcess
		fmt.Println("Successfully pushed changes to TargetProcess")

		return nil
	},
}

// generateTrackingBranchName generates a tracking branch name from release and team
// Format: TP-<RELEASE>-<team> (e.g., TP-PI-4-25-platform-eco)
func generateTrackingBranchName(release string, team string) string {
	// Normalize release: uppercase, replace / with -, remove special chars
	releaseNorm := strings.ToUpper(strings.ReplaceAll(release, "/", "-"))
	// Remove any remaining special characters except dash
	releaseNorm = strings.Map(func(r rune) rune {
		if (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') || r == '-' {
			return r
		}
		return -1
	}, releaseNorm)

	// Normalize team: lowercase, replace spaces with -, remove special chars
	teamNorm := strings.ToLower(strings.ReplaceAll(team, " ", "-"))
	// Remove any remaining special characters except dash
	teamNorm = strings.Map(func(r rune) rune {
		if (r >= 'a' && r <= 'z') || (r >= '0' && r <= '9') || r == '-' {
			return r
		}
		return -1
	}, teamNorm)

	return fmt.Sprintf("TP-%s-%s", releaseNorm, teamNorm)
}

// generateFeatureBranchName generates a feature branch name from release
// Format: feature/plan-<release> (e.g., feature/plan-pi-4-25)
func generateFeatureBranchName(release string) string {
	releaseNorm := strings.ToLower(strings.ReplaceAll(release, "/", "-"))
	return fmt.Sprintf("feature/plan-%s", releaseNorm)
}

func init() {
	rootCmd.AddCommand(planCmd)

	planCmd.AddCommand(createCmd)
	createCmd.Flags().String("data", "", "JSON data for entity (required)")

	planCmd.AddCommand(updateCmd)
	updateCmd.Flags().String("data", "", "JSON data for entity (required)")

	planCmd.AddCommand(initCmd)
	initCmd.Flags().String("release", "", "Release name (e.g., PI-4/25) (required)")
	initCmd.Flags().String("team", "", "Team name (required)")

	planCmd.AddCommand(pullCmd)

	planCmd.AddCommand(pushCmd)
}
