
from datetime import datetime
from textwrap import dedent
from pathlib import Path
import uuid
import asyncio
from google import genai
from agno.media import Image
from agno.workflow import Workflow, Step, Parallel
from agno.workflow.types import StepInput, StepOutput
from agno.db.sqlite import SqliteDb
from agents import create_digest_agent, create_research_agent
from config.settings import DATABASE_FILE, GOOGLE_API_KEY, IMAGES_DIR, AGENTOS_HOST, AGENTOS_PORT
from workflows.notification_manager import get_notification_manager

def generate_cover_image(step_input: StepInput) -> StepOutput:
    """Generate a cover image for the newsletter using Google Gemini and save to filesystem"""
    newsletter_content = step_input.previous_step_content or step_input.input
    print("🎨 Generating cover image for newsletter...")

    try:
        # Extract title (use first non-empty line)
        title = next(
            (line.strip() for line in newsletter_content.split("\n") if line.strip()),
            "Newsletter",
        )

        prompt = (
            f"Create a modern, minimalist, high-quality cover image for a newsletter titled: {title}."
        )
        print(f"📝 Image prompt: {prompt}")

        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
        )

        # Extract image bytes
        image_bytes = None
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_bytes = part.inline_data.data
                print(f"✅ Cover image generated: {len(image_bytes)} bytes")
                break

        if image_bytes is None:
            print("⚠️ No image generated, continuing without cover")
            return StepOutput(content=newsletter_content, success=True)

        # Save image to filesystem
        image_id = str(uuid.uuid4())
        image_filename = f"newsletter_cover_{image_id}.png"
        image_path = IMAGES_DIR / image_filename

        with open(image_path, 'wb') as f:
            f.write(image_bytes)

        print(f"💾 Image saved to: {image_path}")

        # Create image URL (accessible via static files)
        # Use localhost for development, should be configurable for production
        image_url = f"http://{AGENTOS_HOST}:{AGENTOS_PORT}/static/images/{image_filename}"

        # Return Image with URL instead of content
        cover_image = Image(url=image_url, id=image_id)
        print(f"🔗 Image URL: {image_url}")

        return StepOutput(content=newsletter_content, images=[cover_image], success=True)

    except Exception as e:
        print(f"❌ Error generating cover image: {e}")
        import traceback
        traceback.print_exc()
        return StepOutput(content=newsletter_content, success=True)


def save_newsletter(step_input: StepInput) -> StepOutput:
    """Save the generated newsletter with optional cover image and send notification"""
    user_id = (step_input.additional_data or {}).get("user_id", "default")
    session_id = (step_input.additional_data or {}).get("session_id", "")
    run_id = (step_input.additional_data or {}).get("run_id", "")
    enable_notification = (step_input.additional_data or {}).get("enable_notification", False)

    newsletter_content = step_input.previous_step_content or step_input.input
    newsletter_id = f"newsletter_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    has_cover = hasattr(step_input, "images") and step_input.images
    cover_status = "✅ With cover image" if has_cover else "⚠️ No cover image"

    # Extract cover image URL if available
    cover_image_url = None
    if has_cover and step_input.images:
        cover_image_url = step_input.images[0].url if hasattr(step_input.images[0], 'url') else None

    final_output = dedent(f"""
        ✅ Newsletter Generated Successfully!

        Newsletter ID: {newsletter_id}
        User ID: {user_id}
        Generated at: {datetime.now().isoformat()}
        Cover Image: {cover_status}

        {newsletter_content}


    """).strip()

    print(f"💾 Saved newsletter {newsletter_id} ({cover_status})")

    # Send notification if enabled
    if enable_notification and run_id:
        print(f"📬 Sending notification for run {run_id}")
        notification_manager = get_notification_manager()

        # Use asyncio to send notification (workflow executor handles async)
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(
                notification_manager.notify_workflow_completion(
                    run_id=run_id,
                    status="completed",
                    content=newsletter_content,
                    cover_image_url=cover_image_url,
                )
            )
        except Exception as e:
            print(f"⚠️  Failed to send notification: {e}")

    # Pass images through to final output
    return StepOutput(
        content=final_output,
        images=step_input.images if has_cover else None,
        success=True
    )


def create_simple_newsletter_workflow(db: SqliteDb = None) -> Workflow:
    """Simplified newsletter workflow with one agent, image generation, and save"""
    if db is None:
        db = SqliteDb(db_file=DATABASE_FILE)

    # Single agent
    digest_agent = create_digest_agent(db=db)

    # Step 1: Generate newsletter content
    generate_step = Step(
        name="Generate Newsletter",
        agent=digest_agent,
        description="Generate a newsletter based on user's input or topic.",
    )

    # Step 2: Generate cover image
    cover_step = Step(
        name="Generate Cover Image",
        executor=generate_cover_image,
        description="Generate a cover image for the newsletter using Google Gemini.",
    )

    # Step 3: Save newsletter
    save_step = Step(
        name="Save Newsletter",
        executor=save_newsletter,
        description="Save the final newsletter (with optional cover image).",
    )

    workflow = Workflow(
        name="Simple Newsletter Workflow",
        description="Simplified workflow: generate newsletter → create cover → save.",
        db=db,
        steps=[generate_step, cover_step, save_step],
        store_events=True,
    )

    return workflow