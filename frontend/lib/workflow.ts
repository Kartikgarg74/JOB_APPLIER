import { fetchWithRetry } from './fetchWithRetry';
import { API_CONFIG, getServiceUrl } from './config';

export interface WorkflowStatus {
  is_running: boolean;
  last_state_change: number; // Unix timestamp
}

/**
 * Fetches the current status of the agent workflow from the orchestration service.
 * @returns A promise that resolves to the workflow status.
 */
export async function getWorkflowStatus(): Promise<WorkflowStatus> {
  try {
    const url = getServiceUrl('AGENT_ORCHESTRATION_SERVICE', '/workflow/status');
    const response = await fetchWithRetry(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch workflow status: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching workflow status:', error);
    // Return a default "stopped" state on error to prevent UI crashes
    return { is_running: false, last_state_change: 0 };
  }
}

/**
 * Updates the status of the agent workflow (e.g., to pause or resume).
 * @param isRunning - The desired state of the workflow (true for run, false for pause).
 * @returns A promise that resolves to the updated workflow status.
 */
export async function updateWorkflowStatus(isRunning: boolean): Promise<WorkflowStatus> {
  try {
    const url = getServiceUrl('AGENT_ORCHESTRATION_SERVICE', '/workflow/status');
    const response = await fetchWithRetry(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_running: isRunning }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(`Failed to update workflow status: ${errorData.detail}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating workflow status:', error);
    throw error;
  }
}
