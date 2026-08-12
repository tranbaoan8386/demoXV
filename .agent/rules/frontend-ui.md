# DemoXV Frontend UI Rules

## Purpose

Define the product-level visual language for DemoXV frontend work.

These rules describe **what the interface should feel like and how design decisions are made**. They do not replace the implementation rules in `.github/instructions/frontend.instructions.md` or the workflow in `.agent/skills/frontend-design/SKILL.md`.

## Product qualities

DemoXV interfaces should feel:

- professional
- calm
- clear
- information-focused
- trustworthy
- consistent
- suitable for repeated daily use

"Modern" does not mean visually busy. Do not add visual effects simply because they are common in AI-generated interfaces.

## Design principles

### 1. Design for the user's job

Every screen should have one obvious primary task or information goal.

Prioritize:

1. page purpose
2. primary action or primary information
3. supporting information
4. secondary actions
5. low-priority metadata

### 2. Prefer product language over generic patterns

Use the domain to shape hierarchy, grouping and interaction.

For example, a CV/document workflow should feel like a document workspace rather than a generic SaaS dashboard.

### 3. Reuse before invention

Before creating a new visual pattern, inspect adjacent screens and reusable components.

Prefer an established DemoXV pattern unless there is a clear product reason to change it.

### 4. Use restraint

Prefer:

- clear surfaces
- subtle borders
- restrained shadows
- a small and consistent radius scale
- intentional spacing
- one primary accent
- semantic status colors

Avoid by default:

- large decorative gradients
- glassmorphism
- dramatic shadows
- excessive rounded containers
- decorative borders
- random colors
- unnecessary motion
- repetitive card grids

### 5. Make hierarchy visible without decoration

Use size, spacing, grouping, alignment, contrast and position before adding decorative elements.

Do not use color or font weight alone when a stronger structural grouping would communicate the hierarchy better.

## Interaction states

Interactive elements should have appropriate states for the feature:

- default
- hover
- focus
- active/selected
- disabled
- loading
- success
- error
- empty

The default state is not enough for a production UI.

## Responsive behavior

Design desktop, tablet and mobile as intentional compositions.

Do not simply shrink a desktop layout.

Consider:

- navigation collapse
- column-to-stack transitions
- table overflow
- button wrapping
- form grouping
- text truncation
- touch targets

## Accessibility baseline

Use semantic HTML and visible focus states.

Do not rely on color alone for status.

Every interactive control needs a meaningful accessible name.

## Change control

When improving an existing screen:

1. preserve working behavior
2. preserve established product identity
3. improve hierarchy and usability before adding decoration
4. keep changes scoped to the requested feature
5. do not introduce a second visual language

## Definition of done

A frontend change is visually complete when it:

- supports the user's primary task
- looks native to DemoXV
- reuses existing patterns where appropriate
- handles relevant states
- works on mobile
- remains accessible
- avoids generic AI-template aesthetics
