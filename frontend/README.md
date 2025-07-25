# Frontend Codebase Guide

## Code Organization
- **Pages**: All route-level components are in `app/` or `components/pages/`.
- **UI Components**: Reusable UI in `components/ui/`.
- **Business Logic & API**: All API calls and business logic are in `lib/`.
- **Context/Providers**: Shared services (API, auth, theme) are provided via React context in `lib/`.
- **Hooks**: Custom hooks in `hooks/`.

## Dependency Injection
- Use the `ApiProvider` from `lib/api-context.tsx` at the app root.
- Access all API services via the `useApiServices` hook:
  ```tsx
  import { useApiServices } from '@/lib/api-context';
  const { fetchAtsScore, fetchApplications, applyForJob, uploadResume } = useApiServices();
  ```
- This enables easy mocking and testing, and reduces coupling.

## Type Safety
- All state, props, and API responses use explicit TypeScript interfaces.
- Avoid `any` and use generics for reusable hooks/utilities.

## Performance
- Use `useMemo` and `useCallback` for expensive computations and stable callbacks.
- Use Next.js `<Image />` for all images.
- Use dynamic imports (`next/dynamic`) for heavy/rarely-used components.

## Error Handling
- Use error boundaries at the app/page level.
- All async code uses try/catch with typed errors and user-friendly messages.
- API errors are surfaced to users via alerts.

## Accessibility
- Use `aria-*`, `role`, and label attributes for all interactive elements.
- Ensure all forms and buttons are accessible via keyboard and screen readers.

## Best Practices
- All components are functional and use hooks.
- Remove dead code and unused dependencies regularly.
- Group related files (component, types, styles, tests) together.

## Example: Using API Context in a Component
```tsx
import { useApiServices } from '@/lib/api-context';

export function MyComponent() {
  const { fetchApplications } = useApiServices();
  // ...
}
```

---
For more, see the code comments and the main project README.
