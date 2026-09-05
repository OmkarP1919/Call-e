from langgraph.graph import (
    StateGraph,
    START,
    END
)

from app.graph.state import BrokerCallState

from app.graph.nodes import (
    validate_input,
    prepare_call,
    call_e_node,
    check_result,
    store_result_node,
    handle_failure_node
)


builder = StateGraph(
    BrokerCallState
)


builder.add_node(
    "validate_input",
    validate_input
)

builder.add_node(
    "prepare_call",
    prepare_call
)

builder.add_node(
    "call_e",
    call_e_node
)

builder.add_node(
    "check_result",
    check_result
)

builder.add_node(
    "store_result",
    store_result_node
)

builder.add_node(
    "handle_failure",
    handle_failure_node
)


builder.add_edge(
    START,
    "validate_input"
)

builder.add_edge(
    "validate_input",
    "prepare_call"
)

builder.add_edge(
    "prepare_call",
    "call_e"
)

builder.add_edge(
    "call_e",
    "check_result"
)

builder.add_conditional_edges(
    "check_result",
    lambda state:
        "store_result"
        if state.get("call_succeeded")
        else "handle_failure",
    {
        "store_result": "store_result",
        "handle_failure": "handle_failure"
    }
)

builder.add_edge(
    "store_result",
    END
)

builder.add_edge(
    "handle_failure",
    END
)


graph = builder.compile()
