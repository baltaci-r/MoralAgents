MORAL_PROMPTS = {
    'ONBOARDING':(
        "Consider the following moral scenario:\n\n{scenario}\n\n"
        "We will be evaluating how morally acceptable is {subject} decision. "
        "We will be using a 1-7 scale where one means completely unacceptable, 4 means neither morally acceptable nor morally unacceptable, and 7 means completely acceptable. "
        "Imagine the score you provided is \"{onboarding}\". "
        "Respond with a detailed argument that supports your moral acceptability rating, copying the rating at the very end of your response. "
    ),

    'ARGUMENT':(
        "The score you provided prior to the group discussion was \"{onboarding}\". "
        "This is the argument you provided then:\n\nSTART\n\n{argument}\n\nEND\n\n"
    ),

    'DISCUSSION_1':(
        "You are in a discussion with {conversants} about the following moral scenario:\n\n{scenario}\n\n"
        "The goal of the discussion is to come to a group consensus about how morally acceptable {subject} decision was in this case. "
        "You will be using a 1-7 scale where one means completely unacceptable, 4 means neither morally acceptable nor morally unacceptable, and 7 means completely acceptable. "
    ),
    'DISCUSSION_2':(
        "This is the discussion you had so far:\n\nSTART\n\n{history}\n\nEND\n\n"
        "Contribute a detailed response to the conversation. If you think the arguments presented in the discussion warrant it, adjust your opinion accordingly. "
        "Finish your response with the moral acceptability score you think matches your current opinion. " #\n\n\n\n{current_response}\n\n"
        ),
    'EXTRACT_OPINION':(
        "Extract the moral acceptability score at the end of this reply:\n\n{}\n\n"
        "Respond with the score ONLY, if there is no score reported return None"
    ),
    'REFLECTION_1':(
        "You were part of a discussion about the following moral scenario:\n\n{scenario}\n\n"
        "The goal of the discussion was to come to a group consensus about how morally acceptable {subject} decision was in this case. "
        "You use a 1-7 scale where one means completely unacceptable, 4 means neither morally acceptable nor morally unacceptable, and 7 means completely acceptable. "
    ),

    'REFLECTION_2':(
        "This is the discussion you had:\n\nSTART\n\n{history}\n\nEND\n\nReflect on the previous discussion, "
        "then respond with a private, detailed argument followed by the moral acceptability score you think matches your current opinion. "
        "Assume this response will not be shared with the conversants of your earlier discussion. "
        ),
    'REFLECTION_SINGLE':(
        "Consider the following moral scenario:\n\n{scenario}\n\n"
        "We will be evaluating how morally acceptable is {subject} decision. "
        "You use a 1-7 scale where one means completely unacceptable, 4 means neither morally acceptable nor morally unacceptable, and 7 means completely acceptable. "
        "Respond with a private, detailed argument followed by the moral acceptability score you think matches your opinion. "
    )
}

OXFORD_PROMPTS = {
    'ONBOARDING':(
        "Consider the following moral statement:\n\n{scenario}\n\n"
        "We will be evaluating how much you agree with the statement. "
        "We will be using a 1-7 scale where one means you strongly disagree and seven means you strongly agree with the statement. "
        "Imagine the score you provided is \"{onboarding}\". "
        "Respond with a detailed argument that supports your agreement rating, copying the rating at the very end of your response. "
    ),

    'ARGUMENT':(
        "The score you provided prior to the group discussion was \"{onboarding}\". "
        "This is the argument you provided then:\n\nSTART\n\n{argument}\n\nEND\n\n"
    ),

    'DISCUSSION_1':(
        "You are in a discussion with {conversants} about the following statement:\n\n{scenario}\n\n"
        "The goal of the discussion is to come to a group consensus about how much you agree with the statement in this case. "
        "You will be using a 1-7 scale where one means you strongly disagree with the statement and seven means you strongly agree with the statement. "
    ),

    'DISCUSSION_2':(
        "This is the discussion you had so far:\n\nSTART\n\n{history}\n\nEND\n\n"
        "Contribute a detailed response to the conversation. If you think the arguments presented in the discussion warrant it, adjust your opinion accordingly. "
        "Finish your response with the agreement rating you think matches your current opinion. " #\n\n\n\n{current_response}\n\n"
    ),

    'EXTRACT_OPINION':(
        "Extract the agreement rating at the end of this reply:\n\n{}\n\n"
        "Respond with the rating ONLY, if there is no rating reported return None"
    ),

    'REFLECTION_1':(
        "You were part of a discussion about the following statement:\n\n{scenario}\n\n"
        "The goal of the discussion was to come to a group consensus about how much you agree with the statement in this case. "
        "You use a 1-7 scale where one means you strongly disagree with the statement and seven means you strongly agree with the statement."
    ),

    'REFLECTION_2':(
        "This is the discussion you had:\n\nSTART\n\n{history}\n\nEND\n\nReflect on the previous discussion, "
        "then respond with a private, detailed argument followed by your agreement rating you think matches your current opinion. "
        "Assume this response will not be shared with the conversants of your earlier discussion. "
    ),

    'REFLECTION_SINGLE':(
        "Consider the following moral statement:\n\n{scenario}\n\n"
        "We will be evaluating how how much you agree with the statement. "
        "You use a 1-7 scale where one means you strongly disagree with the statement and seven means you strongly agree with the statement. "
        "Respond with a private, detailed argument followed by your agreement rating you think matches your opinion. "
    )
}


def get_prompts(dataset):
    """Return the appropriate prompts based on the dataset name."""
    if dataset == 'oxford_utilitarianism_scale':
        return OXFORD_PROMPTS
    return MORAL_PROMPTS 