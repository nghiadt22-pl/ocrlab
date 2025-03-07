Below is a set of front-end guidelines for OCR Lab that describes the overall UI layout, styling conventions, and design principles. These guidelines should help keep the user interface consistent across all pages and features.

---

## 1. General Design Principles

**Simplicity and Clarity**  
OCR Lab embraces a clean, minimal interface that puts the user’s documents and search functionality at the forefront. Each page includes only the essential elements and highlights important actions like “Upload Files” or “Search.”

**Consistency**  
Common UI patterns (such as buttons, form fields, cards, and navigation menus) share the same look and feel across the application. Colors, typography, and icon styles are consistent in order to strengthen brand recognition and reduce cognitive load for users.

**Accessibility**  
Readability is key. Text is sized and colored to meet accessibility standards, and sufficient contrast is maintained between foreground elements (like text and icons) and the background. Spacing is generous to allow easy reading and clicking.

**Responsive Layout**  
All pages must adapt gracefully to different viewports. Sidebars collapse or transform on smaller screens, and tables or file lists become scrollable when there is limited horizontal space.

---

## 2. Layout and Navigation

1. **Top-Level Navigation**  
   A left sidebar (or top navbar on mobile) houses the primary navigation links:  
   - **Dashboard**  
   - **Documents**  
   - **Billing**  
   - **Preferences**  
   The user profile area is at the bottom of the sidebar, showing the user’s name and email.

2. **Main Content Area**  
   The center area displays the primary content for each section, such as a list of folders and documents or the usage dashboard. Key actions, like “Upload Files,” typically appear in the upper-right corner so they are easy to find.

3. **Search Bar**  
   A prominent “Search Documents” bar is placed in the top-right or on a dedicated “Search” page. This promotes the app’s main function of quickly finding relevant document excerpts.

4. **Status/Processing Queue**  
   The dashboard, as well as the dedicated “Documents” page, shows files in a processing queue with clear status indicators (pending, processing, complete).

5. **Responsive Patterns**  
   On smaller screens, the sidebar becomes a collapsible menu, and content reflows to vertical stacks. Modals and dialogs should also scale suitably for mobile usage.

---

## 3. Color Palette

OCR Lab adopts a light background with dark text, accented by a navy or dark blue sidebar. Below is the recommended palette:

- **Primary Background**: `#F9FAFB` (very light gray)  
- **Primary Text**: `#111827` (dark gray/near-black) for headings, `#374151` for regular text  
- **Accent / Brand**: `#1E3A8A` (navy/dark blue) used for the left navigation background, highlights, and primary buttons if desired  
- **Button / Element Background**: `#FFFFFF` (pure white) for form fields and cards  
- **Accent Hover / Lighter Shade**: `#3B82F6` (blue) for hover states or slight emphasis  
- **Border / Divider**: `#E5E7EB` (light gray) for lines and subtle dividers  
- **Success**: `#10B981` (green) for successful file processing  
- **Warning / Pending**: `#F59E0B` (amber) or `#EAB308` for items in queue or partial usage  
- **Error**: `#EF4444` (red) for error states or critical alerts  

Keep color usage deliberate. The brand or accent colors should draw attention to interactive elements (buttons, links, icons for file statuses) without overwhelming the page.

---

## 4. Typography

**Primary Font:**  
- Use **Inter**, a modern and highly readable font optimized for user interfaces. If Inter is not available, fall back to system defaults like `Helvetica Neue`, `Arial`, or `sans-serif`.

**Font Weights:**  
- **Bold (700 or 600)** for titles and headlines.  
- **Regular (400)** for general body text.  
- **Medium (500)** for subheadings or text that needs a bit more emphasis.

**Font Sizes:**  
- **Heading (H1/H2/H3):** 1.25rem to 2rem (20px to 32px) depending on importance.  
- **Body Text:** 1rem (16px) to ensure comfortable reading.  
- **Small Labels:** 0.875rem (14px) for secondary information.

Ensure text aligns well with icons and other UI elements, with enough line height (at least 1.4) for legibility.

---

## 5. Icons

**Icon Style:**  
- Use a consistent icon library such as [Lucide](https://lucide.dev/) or [Heroicons](https://heroicons.com/) for simple, outline-based icons that match a modern UI look.  
- Icons should generally have a stroke weight of around 1.5–2 px to remain sharp and clear.

**Usage Guidelines:**  
- Keep icons minimal: use them primarily to clarify actions (e.g., upload, search, user profile) or indicate status (e.g., check, error, refresh).  
- Place icons to the left of text labels or alone in circular buttons for key actions.  
- Match icon color to the text or accent color for a cohesive appearance.

---

## 6. Components and Styling

1. **Buttons**  
   - **Primary Button**: Dark or brand-colored background (#1E3A8A) with white text (#FFFFFF).  
   - **Secondary Button**: Light background (#FFFFFF) with border (#E5E7EB) and dark text (#111827).  
   - **Hover States**: Slight darkening or lightening of the background color.  
   - **Disabled State**: Lower opacity (e.g., 50%) or a clearly muted tone.

2. **Cards / Panels**  
   - White backgrounds (#FFFFFF) with soft shadows or subtle border (#E5E7EB).  
   - Enough padding (16–24px) and consistent spacing between items.

3. **Forms / Inputs**  
   - White backgrounds with a light gray border.  
   - Rounded corners (4px radius) for a modern look.  
   - Clear placeholder text and label.  
   - Focus State: A subtle blue border highlight (#3B82F6 or #2563EB).

4. **Navigation Sidebar**  
   - Navy background (#1E3A8A) or a very dark gray (#111827).  
   - Light or white text (#F9FAFB or #E5E7EB).  
   - Active link indicated by a bolder background or highlight on the left edge.  
   - Small icons next to navigation items for quick recognition.

5. **Data Representation**  
   - Use progress bars and numeric counters for usage stats (e.g., pages processed, queries made).  
   - Different statuses (Queued, Processing, Completed) displayed with icons (clock, refresh, check mark) and color-coded labels.

6. **Spacing System**  
   - A base spacing unit of **4px** or **8px** is recommended. For consistency, use multiples (e.g., 4, 8, 12, 16, 24, etc.) for margins, padding, and gap sizes.

---

## 7. Practical Examples

1. **Login Page**  
   - White background for the form, brand color or dark text for the heading, subtle shadow to separate the form container from the background.  
   - Primary button stands out with a dark navy background and white text.

2. **Dashboard**  
   - Usage stats in clearly labeled cards or bars.  
   - Processing queue with each file showing an icon and status color.  
   - Minimal use of borders, relying instead on spacing and subtle shades to delineate sections.

3. **Document Upload**  
   - Drag-and-drop area with dashed border (#E5E7EB).  
   - File list below with status icons and a small label for file size and folder.  
   - Folder dropdown using a white background and a dark navy highlight for selected items.

4. **Search Page**  
   - Large, clearly visible search input.  
   - Dropdown toggle for “Folder” vs. “File.”  
   - Search history displayed in collapsible panels with a small timestamp.

---

## 8. Implementation Tips

- **Tailwind CSS**: If you use Tailwind, define a custom config to incorporate the color palette, fonts, and spacing. This reduces the need for repeated inline styles and ensures consistency across components.  
- **shadcn/ui**: As recommended in the product docs, these pre-built components align with modern design patterns and can be customized with Tailwind to match the OCR Lab look and feel.  
- **Responsive Testing**: Always preview your pages on various screen widths (mobile, tablet, desktop) to confirm the layout adapts properly.  
- **Accessibility Checks**: Use tools like Axe or Lighthouse to ensure sufficient color contrast and correct semantic HTML structures.

---

## 9. Summary

By adhering to these guidelines, the OCR Lab front-end will present a cohesive user experience. The focus remains on simplicity, clarity, and modern design practices. Use the recommended color palette, typography, and icon set consistently, and maintain a unified spacing system. Each page—from login to dashboard to document search—should feel like part of the same seamless journey.