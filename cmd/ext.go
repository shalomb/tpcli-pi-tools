package cmd

import (
	"fmt"
	"os"
	"os/exec"

	"github.com/spf13/cobra"
)

var extCmd = &cobra.Command{
	Use:   "ext <list|tool> [args...]",
	Short: "Run or list external extension scripts",
	Long: `Manage external extension scripts (e.g., art-dashboard, team-deep-dive).

Examples:
  tpcli ext list
  tpcli ext team-deep-dive --team "Cloud Enablement & Delivery"`,
	Args: cobra.MinimumNArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		if args[0] == "list" {
			// Logical grouping for discoverability (collate by type: art-*, pi-*, team-*)
			candidates := []string{
				// ART-level scripts
				"art-dashboard",
				// PI/Release-level scripts
				"pi-objectives",
				"pi-status",
				// Team-level scripts
				"team-analysis",
				// Legacy aliases for backwards compatibility
				"objective-deep-dive",
				"release-status",
				"team-deep-dive",
			}
			found := []string{}
			for _, name := range candidates {
				if p, err := exec.LookPath(name); err == nil {
					found = append(found, fmt.Sprintf("%s -> %s", name, p))
				}
			}
			if len(found) == 0 {
				fmt.Println("No extensions found in PATH. Install tools to ~/.local/bin or ensure they are in PATH.")
				return nil
			}
			for _, f := range found {
				fmt.Println(f)
			}
			return nil
		}

		tool := args[0]
		toolArgs := args[1:]
		path, err := exec.LookPath(tool)
		if err != nil {
			return fmt.Errorf("extension not found in PATH: %s", tool)
		}

		c := exec.Command(path, toolArgs...)
		c.Stdin = os.Stdin
		c.Stdout = os.Stdout
		c.Stderr = os.Stderr
		if err := c.Run(); err != nil {
			if exitErr, ok := err.(*exec.ExitError); ok {
				return fmt.Errorf("command exited with status %d", exitErr.ExitCode())
			}
			return fmt.Errorf("running extension: %w", err)
		}
		return nil
	},
}

func init() {
	rootCmd.AddCommand(extCmd)
}
