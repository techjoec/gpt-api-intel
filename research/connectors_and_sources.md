# Connectors, Sources, and Integrations

Keys related to data connectors, selected sources, and plugin-style auth flows.

| Constant | Key | Notes |
| --- | --- | --- |
| `t.SelectedSources` | `oai/apps/connectors/selectedSources` | Array of enabled knowledge sources for contextual answers. |
| `t.SelectedGithubRepos` | `oai/apps/connectors/selectedGithubRepos` | GitHub repositories linked to the account. |
| `t.ConnectorOAuthFlowType` | `oai/apps/connectors/oauthFlowType` | Remembers the last OAuth flow variant (browser vs. device code). |
| `t.PluginsAuthRedirect` | `oai/apps/plugins/authRedirect` | Holds redirect state during plugin authentication. |
| `t.FinchAdminNotified` | `oai/apps/finchAdminNotified` | Records that Finch admin has been notified (avoids duplicate alerts). |
| `vK.hasSeenConnectorsNuxModal` | `oai/apps/hasSeenConnectorsNuxModal` | Onboarding modal for connectors. |
| `vK.hasSeenGoogleConnectorsNuxModal` | `oai/apps/hasSeenGoogleConnectorsNuxModal` | Google-specific connector onboarding. |
| `vK.hasSeenConnectorsSourcesPillTooltip` | `oai/apps/hasSeenConnectorsSourcesPillTooltip` | Tooltip gating for the sources pill. |
| `vK.hasSeenConnectorsUpgradeFileAccessModal` | `oai/apps/hasSeenConnectorsUpgradeFileAccessModal` | Guides the file-access upgrade modal. |
| `vK.hasSeenContextualAnswerGoogleSyncFinished` | `oai/apps/hasSeenContextualAnswerGoogleSyncFinished` | Marks the post-sync completion notice. |
| `t.CARecommendedPromptsUpsell` | `oai/apps/caRecommendedPromptsUpsell` | Recommended prompts upsell for contextual answers. |
| `t.WorkspaceDiscoveryInfo` | `oai/apps/workspaceDiscoveryInfo` | (Also in onboarding doc) includes connector hints when present. |

