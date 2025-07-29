import { AppLayout } from "@/components/layout/app-layout"
import { ApplicationsTracker } from "@/components/pages/applications-tracker"

export default function ApplicationsPage() {
  return (
    <AppLayout>
      <ApplicationsTracker userId="1" />
    </AppLayout>
  )
}
