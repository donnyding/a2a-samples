import functools

import mesop as me

from state.state import AppState, StateMessage


def toggle_thought(message_id: str, e: me.ClickEvent):
    """Toggle thought expansion state for a specific message."""
    app_state = me.state(AppState)
    if message_id in app_state.thought_expanded:
        app_state.thought_expanded.remove(message_id)
    else:
        app_state.thought_expanded.append(message_id)


@me.component
def chat_bubble(message: StateMessage, key: str):
    """Chat bubble component"""
    app_state = me.state(AppState)
    show_progress_bar = (
        message.message_id in app_state.background_tasks
        or message.message_id in app_state.message_aliases.values()
    )
    progress_text = ''
    if show_progress_bar:
        progress_text = app_state.background_tasks[message.message_id]
    if not message.content:
        print('No message content')

    # Check if this message has thinking (agent with 2 parts)
    num_parts = len(message.content)
    is_agent_with_thought = message.role == 'agent' and num_parts == 2

    # Track expanded state for this specific message
    is_expanded = message.message_id in app_state.thought_expanded

    for idx, pair in enumerate(message.content):
        content, media_type = pair[0], pair[1]

        # First part of agent message with 2 parts is thought
        is_thought_part = is_agent_with_thought and idx == 0
        # Second part or single part is response content
        is_response_part = (is_agent_with_thought and idx == 1) or (not is_agent_with_thought)

        chat_box(
            content,
            media_type,
            message.role,
            key,
            is_thought_part,
            is_response_part,
            is_expanded,
            functools.partial(toggle_thought, message.message_id),
            progress_bar=show_progress_bar,
            progress_text=progress_text,
        )


@me.component
def chat_box(
    content: str,
    media_type: str,
    role: str,
    key: str,
    is_thought_part: bool,
    is_response_part: bool,
    is_expanded: bool,
    on_toggle,
    progress_bar: bool,
    progress_text: str,
):
    with me.box(
        style=me.Style(
            display='flex',
            justify_content=('space-between' if role == 'agent' else 'end'),
            min_width=500,
        ),
        key=key,
    ):
        with me.box(
            style=me.Style(display='flex', flex_direction='column', gap=5)
        ):
            if media_type == 'image/png':
                img_src = content if '/message/file' in content else 'data:image/png;base64,' + content
                me.image(
                    src=img_src,
                    style=me.Style(
                        width='50%',
                        object_fit='contain',
                    ),
                )
            elif is_thought_part:
                # Render thinking content as collapsible section
                with me.box(
                    style=me.Style(
                        display='flex',
                        align_items='center',
                        gap=8,
                        margin=me.Margin(top=5, left=0, right=0, bottom=3),
                    )
                ):
                    me.button(
                        '▼' if is_expanded else '▶',
                        on_click=on_toggle,
                        type='flat',
                        style=me.Style(
                            font_size=12,
                            height=24,
                            padding=me.Padding(left=4, right=4),
                            min_width=24,
                        ),
                    )
                    me.text(
                        'Thought',
                        style=me.Style(
                            font_weight='bold',
                            font_size=13,
                            color=me.theme_var('on-surface-variant'),
                        )
                    )

                if is_expanded:
                    me.markdown(
                        content,
                        style=me.Style(
                            font_family='Google Sans',
                            font_size=13,
                            color=me.theme_var('on-surface-variant'),
                            font_style='italic',
                            padding=me.Padding(left=10, right=10, top=5, bottom=5),
                            background=me.theme_var('surface-container-low'),
                            border_radius=8,
                            margin=me.Margin(top=0, left=0, right=0, bottom=5),
                        ),
                    )
            elif is_response_part:
                # Normal message rendering
                me.markdown(
                    content,
                    style=me.Style(
                        font_family='Google Sans',
                        box_shadow=(
                            '0 1px 2px 0 rgba(60, 64, 67, 0.3), '
                            '0 1px 3px 1px rgba(60, 64, 67, 0.15)'
                        ),
                        padding=me.Padding(top=1, left=15, right=15, bottom=1),
                        margin=me.Margin(top=5, left=0, right=0, bottom=5),
                        background=(
                            me.theme_var('primary-container')
                            if role == 'user'
                            else me.theme_var('secondary-container')
                        ),
                        border_radius=15,
                    ),
                )
    if progress_bar:
        with me.box(
            style=me.Style(
                display='flex',
                justify_content=('space-between' if role == 'user' else 'end'),
                min_width=500,
            ),
            key=key,
        ):
            with me.box(
                style=me.Style(display='flex', flex_direction='column', gap=5)
            ):
                with me.box(
                    style=me.Style(
                        font_family='Google Sans',
                        box_shadow=(
                            '0 1px 2px 0 rgba(60, 64, 67, 0.3), '
                            '0 1px 3px 1px rgba(60, 64, 67, 0.15)'
                        ),
                        padding=me.Padding(top=1, left=15, right=15, bottom=1),
                        margin=me.Margin(top=5, left=0, right=0, bottom=5),
                        background=(
                            me.theme_var('primary-container')
                            if role == 'agent'
                            else me.theme_var('secondary-container')
                        ),
                        border_radius=15,
                    ),
                ):
                    if not progress_text:
                        progress_text = 'Working...'
                    me.text(
                        progress_text,
                        style=me.Style(
                            padding=me.Padding(
                                top=1, left=15, right=15, bottom=1
                            ),
                            margin=me.Margin(top=5, left=0, right=0, bottom=5),
                        ),
                    )
                    me.progress_bar(color='accent')