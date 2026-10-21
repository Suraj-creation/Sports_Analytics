# 04 --- Design System, Accessibility, and Content Guidelines

## 1. Visual direction

Design for a modern, premium sports product that feels energetic but
calm. It should combine the clarity of a sports dashboard with the
warmth of a personal memory product.

Recommended visual language: - Deep ink / charcoal text. - Warm
off-white or neutral canvas. - One vivid badminton-inspired accent
color. - A secondary cool accent for analytics. - Green reserved for
verified positive status, not generic decoration. - Amber for
uncertainty or attention. - Red only for destructive actions or genuine
errors. - Rounded cards with restrained borders. - High-quality
thumbnails and generous whitespace. - Charts that prioritize readability
over decoration.

Do not use neon gradients everywhere, excessive glassmorphism, or a wall
of cards. Use visual emphasis for one primary action and one main
insight per screen.

## 2. Typography

-   Use a highly readable UI sans-serif.
-   Strong page titles, concise card headings, readable body copy.
-   Numeric values should use tabular figures where possible.
-   Use no more than three typographic levels within a single card.
-   Avoid tiny axis labels and all-caps paragraphs.
-   Do not communicate confidence using color alone.

## 3. Spacing and layout

Use a consistent spacing scale, for example 4 / 8 / 12 / 16 / 24 / 32 /
48 / 64 px. - Standard card padding: 16--24 px. - Form groups: clear
vertical rhythm. - Wide analytics pages may use a 12-column grid. - Keep
reading text at a comfortable line length. - Preserve a clear primary
action at the top of long pages. - On mobile, cards stack; avoid
horizontal scrolling except for intentionally scrollable timelines.

## 4. Core components

### App shell

Sidebar/bottom navigation, page header, mode switch, profile menu,
processing status.

### Button hierarchy

-   Primary: one key action per view.
-   Secondary: alternate action.
-   Tertiary/text: low-emphasis navigation.
-   Destructive: explicit and separated. Buttons must have loading,
    disabled, hover, focus, and pressed states.

### Session card

Thumbnail or sport icon, date, singles/doubles, status, verified score
if available, highlight count, open action.

### Highlight card

Thumbnail, event title, session date, participant, duration if known,
verification/confidence marker, favorite action. Never autoplay video in
a grid.

### Metric card

Metric name, value, unit, baseline/change, sample size, status, info
action, evidence link.

### Confidence badge

Use text such as "Verified", "Estimate", "Needs review", or
"Insufficient evidence". Pair with an icon and explanatory text.

### Chart card

Title, date range, chart, accessible summary, sample size, caveat,
source/evidence link.

### Empty state

Short explanation, one next step, optional illustration. Avoid blaming
the user for having no data.

### Feedback panel

Small, dismissible, non-blocking, with "Useful", "Not useful", and
"Report an issue".

### Consent control

Separate toggle per purpose, a concise explanation, current status, and
link to full details.

### Clip player

Accessible controls, captions/metadata where applicable, keyboard
operation, playback speed only if supported, share/save actions outside
the video canvas.

### Filter bar

Clear current filters, visible active-filter count, sensible defaults,
mobile drawer.

## 5. Data visualization rules

-   Use a chart only when it helps answer a question.
-   Every chart needs a title that states the subject, not "Analytics".
-   Include unit, time range, sample size, and baseline.
-   Provide a text summary and/or accessible table.
-   Do not imply a continuous trend from sparse points.
-   Use zero-based axes for counts unless a clear reason exists
    otherwise.
-   Avoid dual axes unless necessary.
-   Distinguish missing values from zero.
-   Use direct labels where possible.
-   Do not use red/green alone to show good/bad performance.
-   A scoreline and a performance metric must be visually distinct.
-   When confidence is low, avoid a chart that makes the result look
    precise.

## 6. Accessibility

Target WCAG 2.2 AA as an implementation goal. - Keyboard navigation for
all controls. - Visible focus ring. - Semantic heading hierarchy. -
Accessible names for icon-only controls. - Minimum 4.5:1 contrast for
normal text where applicable. - Touch targets ideally at least 44 × 44
CSS pixels. - Captions or text alternatives for important video content
when available. - Respect reduced-motion settings. - Never rely on hover
to expose essential information. - Screen-reader summaries for charts. -
Avoid flashing, rapidly pulsing status, or forced animation. - Form
errors must be associated with fields. - Keep focus predictable after
dialogs close.

## 7. Content voice

Voice: encouraging, clear, respectful, grounded, never patronizing.

Use: - "Here's a moment worth replaying." - "A new personal best in your
observed sessions." - "You kept this rally going for 11 shots." - "This
estimate is based on 8 classifiable rallies." - "We need more comparable
sessions before showing a trend." - "Want to explore this pattern?"

Avoid: - "You are bad at..." - "You failed..." - "Your partner
caused..." - "You are definitely improving" when evidence is weak. -
"You burned exactly X calories" without validated measurement. - "You
looked angry/confident/tired" based only on video. - "You must play
tomorrow to keep your streak."

## 8. Microcopy standards

### Loading

"Preparing your session recap..."\
"Checking player and rally labels..."\
"Some insights are ready while the rest finish processing."

### Empty state

"Your badminton story starts with your first session."\
"Once we have comparable sessions, your progress view will begin to take
shape."

### Low confidence

"We couldn't identify this event reliably enough to include it as a
verified highlight."\
"Review participant labels to improve the accuracy of your recap."

### Correction

"Thanks for flagging this. Your report will help us review the event."\
Only promise correction if the backend actually supports review and
resolution.

### Sharing

"Choose who can see this clip."\
"Sharing this clip does not change your video-analysis or
model-improvement settings."

## 9. Motion and transitions

-   Use motion to clarify hierarchy or state change, not to decorate.
-   Keep transitions short and optional.
-   No confetti for ordinary metrics; use restrained celebration for
    meaningful personal records.
-   Respect reduced-motion.
-   Never animate performance scores in a way that implies false
    precision.

## 10. Responsive behavior

Desktop: - Persistent sidebar. - Wide charts and multi-column layouts. -
Side panel for rally details.

Tablet: - Collapsible sidebar. - Two-column cards where practical. -
Filters remain visible if space allows.

Mobile: - Bottom navigation. - Single-column cards. - Filters in
sheets. - Sticky primary action only when it does not cover content. -
Video player and clip controls sized for touch. - Tables transform into
labeled rows or horizontally scroll only when necessary.
