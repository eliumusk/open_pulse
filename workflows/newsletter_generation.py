"""
Newsletter Generation Workflow
Automatically generates personalized newsletters based on user interests and memories
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from textwrap import dedent
from io import BytesIO

from google import genai
from PIL import Image as PILImage

from agno.media import Image
from agno.workflow import Workflow, Step, Parallel
from agno.workflow.types import StepInput, StepOutput
from agno.db.sqlite import SqliteDb

from agents import create_digest_agent, create_research_agent
from config.settings import DATABASE_FILE, GOOGLE_API_KEY


def extract_user_context(step_input: StepInput) -> StepOutput:
    """
    Step 1: Extract user context from memories and session history

    This function retrieves:
    - User memories (long-term interests)
    - Recent session topics
    - User preferences

    Args:
        step_input: Contains user_id and session_id in additional_data (optional)

    Returns:
        StepOutput with user context summary
    """
    # Safely get additional_data (might be None when called from AgentOS UI)
    additional_data = step_input.additional_data or {}
    user_id = additional_data.get("user_id", "default_user")
    session_id = additional_data.get("session_id")

    print(f"📊 Extracting context for user: {user_id}")

    # Get interests from input message
    # When called from AgentOS UI, the message is in step_input.input
    interests = step_input.input or "technology, AI, and science"

    # TODO: In production, fetch from database using user_id
    # For MVP, we'll use the input message as context
    user_context = {
        "user_id": user_id,
        "session_id": session_id,
        "interests": interests,
        "timestamp": datetime.now().isoformat(),
    }

    context_summary = dedent(f"""
        User Context Summary:
        - User ID: {user_id}
        - Session ID: {session_id or 'N/A'}
        - Interests: {user_context['interests']}
        - Generated at: {user_context['timestamp']}

        Please research and generate a newsletter covering these topics.
    """).strip()

    print(f"✅ Context extracted: {len(context_summary)} characters")

    # Note: StepOutput doesn't support additional_data
    # We include the context in the content itself
    return StepOutput(
        content=context_summary,
        success=True,
    )


def generate_cover_image(step_input: StepInput) -> StepOutput:
    """
    Step 4: Generate a cover image for the newsletter using Google Gemini

    This function:
    1. Extracts the newsletter title/topic from the content
    2. Creates a prompt for image generation
    3. Calls Google Gemini 2.5 Flash Image model
    4. Returns the newsletter content with the generated cover image

    Args:
        step_input: Contains the generated newsletter content

    Returns:
        StepOutput with newsletter content and cover image
    """
    newsletter_content = step_input.previous_step_content or step_input.input

    print(f"🎨 Generating cover image for newsletter...")

    try:
        # Extract title from newsletter (first line after markdown header)
        lines = newsletter_content.split('\n')
        title = "Newsletter"
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('*'):
                title = line.strip()[:100]  # First 100 chars
                break

        # Create prompt for image generation
        # Simple prompt based on title - you can adjust this later
        prompt = f"Create a modern, professional newsletter cover image for: {title}. Style: clean, minimalist, tech-focused, high quality."

        print(f"📝 Image prompt: {prompt[:100]}...")

        # Initialize Google Gemini client
        client = genai.Client(api_key=GOOGLE_API_KEY)

        # Generate image
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
        )

        # Extract image data
        cover_image = None
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # Get image bytes
                image_bytes = part.inline_data.data

                # Create Agno Image object
                cover_image = Image(
                    content=image_bytes,
                    mime_type="image/png",
                )

                print(f"✅ Cover image generated: {len(image_bytes)} bytes")
                break

        if cover_image is None:
            print("⚠️  No image generated, continuing without cover")
            return StepOutput(
                content=newsletter_content,
                success=True,
            )

        # Return newsletter content with cover image
        return StepOutput(
            content=newsletter_content,
            images=[cover_image],  # Agno will store this in session_data
            success=True,
        )

    except Exception as e:
        print(f"❌ Error generating cover image: {e}")
        print("⚠️  Continuing without cover image")
        # Graceful degradation - return newsletter without image
        return StepOutput(
            content=newsletter_content,
            success=True,
        )


def save_newsletter(step_input: StepInput) -> StepOutput:
    """
    Step 5: Save the generated newsletter (with cover image) to database

    The newsletter and cover image are automatically saved by Agno's workflow storage system.
    This step just returns the complete newsletter content for display.

    Args:
        step_input: Contains the generated newsletter content and cover image

    Returns:
        StepOutput with the complete newsletter content and cover image
    """
    # Safely get additional_data (might be None when called from AgentOS UI)
    additional_data = step_input.additional_data or {}
    user_id = additional_data.get("user_id", "default_user")
    newsletter_content = step_input.previous_step_content or step_input.input

    print(f"💾 Newsletter ready for user: {user_id}")

    newsletter_id = f"newsletter_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Check if cover image is available
    has_cover = hasattr(step_input, 'images') and step_input.images and len(step_input.images) > 0
    cover_status = "✅ With cover image" if has_cover else "⚠️  No cover image"

    # Return the COMPLETE newsletter content, not just a preview
    # The workflow storage system will automatically save this to the database
    complete_output = dedent(f"""
        ✅ Newsletter Generated Successfully!

        Newsletter ID: {newsletter_id}
        User ID: {user_id}
        Generated at: {datetime.now().isoformat()}
        Cover Image: {cover_status}

        ═══════════════════════════════════════════════════════════════

        {newsletter_content}

        ═══════════════════════════════════════════════════════════════

        📊 Stats: {len(newsletter_content)} characters
    """).strip()

    print(f"✅ Newsletter ready: {newsletter_id} ({len(newsletter_content)} chars, {cover_status})")

    # Return the complete content with images - Agno will store this in the database
    # Images from previous step are automatically propagated
    return StepOutput(
        content=complete_output,
        success=True,
    )


def create_newsletter_workflow(db: SqliteDb = None) -> Workflow:
    """
    Create the Newsletter Generation Workflow

    Workflow Structure:
    1. Extract user context (Function)
    2. Research phase (Parallel - multiple research agents)
    3. Generate newsletter (Digest Agent)
    4. Generate cover image (Function - Google Gemini)
    5. Save newsletter with cover (Function)

    Args:
        db: Database instance (optional)

    Returns:
        Workflow: Configured newsletter generation workflow
    """
    if db is None:
        # Use Agno's default table names
        db = SqliteDb(db_file=DATABASE_FILE)
    
    # Create agents
    digest_agent = create_digest_agent(db=db)
    research_agent_1 = create_research_agent(db=db)
    research_agent_2 = create_research_agent(db=db)
    
    # Define workflow steps
    
    # Step 1: Extract user context
    extract_context_step = Step(
        name="Extract User Context",
        executor=extract_user_context,
        description="Extract user interests and preferences from memories and sessions",
    )
    
    # Step 2: Parallel research phase
    research_step_1 = Step(
        name="Research Latest Developments",
        agent=research_agent_1,
        description="Research the latest developments in user's topics of interest",
    )
    
    research_step_2 = Step(
        name="Research Academic Papers",
        agent=research_agent_2,
        description="Search for relevant academic papers and research",
    )
    
    research_phase = Parallel(
        research_step_1,
        research_step_2,
        name="Research Phase",
    )
    
    # Step 3: Generate newsletter
    generate_newsletter_step = Step(
        name="Generate Newsletter",
        agent=digest_agent,
        description="Generate a personalized newsletter based on research findings",
    )

    # Step 4: Generate cover image
    generate_cover_step = Step(
        name="Generate Cover Image",
        executor=generate_cover_image,
        description="Generate a cover image for the newsletter using Google Gemini",
    )

    # Step 5: Save newsletter with cover
    save_newsletter_step = Step(
        name="Save Newsletter",
        executor=save_newsletter,
        description="Save the generated newsletter with cover image to database",
    )
    
    # Create workflow
    workflow = Workflow(
        name="Newsletter Generation Workflow",
        description=dedent("""
            Automatically generates personalized newsletters with cover images for users based on their interests.

            This workflow:
            1. Extracts user context from memories and session history
            2. Conducts parallel research from multiple sources
            3. Generates a well-structured newsletter
            4. Creates a cover image using Google Gemini
            5. Returns the complete newsletter with cover image

            The complete newsletter and cover image are automatically stored in the database by Agno's storage system.
        """).strip(),
        db=db,
        store_events=True,  # Store all workflow events for debugging and analysis
        steps=[
            extract_context_step,
            research_phase,
            generate_newsletter_step,
            generate_cover_step,  # New step for cover image generation
            save_newsletter_step,
        ],
    )
    
    return workflow


# For testing
if __name__ == "__main__":
    print("🧪 Testing Newsletter Generation Workflow")
    print("=" * 60)
    
    workflow = create_newsletter_workflow()
    
    # Test with sample input
    result = asyncio.run(
        workflow.arun(
            input="I'm interested in AI, quantum computing, and space exploration",
            additional_data={
                "user_id": "test_user_123",
                "session_id": "test_session_456",
            },
            stream=False,
        )
    )
    
    print("\n" + "=" * 60)
    print("✅ Workflow completed!")
    print(f"Result: {result.content[:500]}...")

