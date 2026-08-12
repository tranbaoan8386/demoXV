---
applyTo: "apps/**/*.{ts,tsx,css}"
---

# DemoXV Frontend Engineering Instructions

## Scope

These instructions apply to React frontend code under `apps/`.

## Stack

- React
- Vite
- TypeScript
- Tailwind CSS

Use the existing project configuration. Do not replace the stack or introduce a second styling system without an explicit requirement.

## TypeScript

- Use strict typing.
- Do not use `any`.
- Prefer domain-specific types.
- Use `unknown` for genuinely unknown external data and narrow it before use.
- Keep API/data types explicit at boundaries.

## React

- Use functional components.
- Keep components focused on one responsibility.
- Keep page components readable; extract components when responsibility or reuse justifies it.
- Keep business/data concerns separate from presentational concerns when the existing architecture supports that separation.
- Reuse existing hooks, utilities and components before creating alternatives.

## Styling

- Use Tailwind CSS and existing project utilities/tokens.
- Reuse established color, spacing, radius and depth patterns.
- Do not create arbitrary design tokens for one component.
- Do not introduce a new component library for a local UI problem.
- Avoid inline styles when the existing design system can express the value.

## Data and API boundaries

- Keep API access in the established service/hook layer.
- Validate or narrow external data before rendering it.
- Do not mix transport details into reusable presentational components.
- Represent loading, empty, error and success states when the feature can produce them.

## Responsive UI

Every new or substantially changed screen must have intentional behavior for desktop, tablet and mobile.

## Accessibility

- Prefer semantic HTML.
- Provide meaningful labels and accessible names.
- Keep keyboard focus visible.
- Do not rely on color alone.
- Use correct button/link semantics.
- Ensure interactive controls remain usable on small screens.

## Dependencies

Do not add a dependency for a small problem that can be solved with existing code or platform capabilities.

## Before coding

Inspect, in order:

1. the target page/component
2. nearby routes and components
3. existing design tokens and styles
4. existing data/API patterns
5. relevant tests
6. `.agent/rules/frontend-ui.md`
7. `.agent/skills/frontend-design/SKILL.md` when the task is a new page or substantial UI work

## Before finishing

Check the smallest relevant validation set available:

- type checking
- lint/formatting when configured
- relevant tests
- responsive behavior
- loading/empty/error states
- accessibility basics
- visual consistency with nearby screens
