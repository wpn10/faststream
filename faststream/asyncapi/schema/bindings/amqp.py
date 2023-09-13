from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class Queue(BaseModel):
    """A class to represent a queue.

    Attributes:
        name : name of the queue
        durable : indicates if the queue is durable
        exclusive : indicates if the queue is exclusive
        autoDelete : indicates if the queue should be automatically deleted
        vhost : virtual host of the queue (default is "/")
    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """

    name: str
    durable: bool
    exclusive: bool
    autoDelete: bool
    vhost: str = "/"


class Exchange(BaseModel):
    """A class to represent an exchange.

    Attributes:
        name : name of the exchange (optional)
        type : type of the exchange, can be one of "default", "direct", "topic", "fanout", "headers"
        durable : whether the exchange is durable (optional)
        autoDelete : whether the exchange is automatically deleted (optional)
        vhost : virtual host of the exchange, default is "/"
    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """

    name: Optional[str] = None
    type: Literal["default", "direct", "topic", "fanout", "headers"]
    durable: Optional[bool] = None
    autoDelete: Optional[bool] = None
    vhost: str = "/"


class ServerBinding(BaseModel):
    """A class to represent a server binding.

    Attributes:
        bindingVersion : version of the binding (default: "0.2.0")
    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """

    bindingVersion: str = "0.2.0"


class ChannelBinding(BaseModel):
    """A class to represent channel binding.

    Attributes:
        is_ : Type of binding, can be "queue" or "routingKey"
        bindingVersion : Version of the binding
        queue : Optional queue object
        exchange : Optional exchange object
    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """

    is_: Literal["queue", "routingKey"] = Field(..., alias="is")
    bindingVersion: str = "0.2.0"
    queue: Optional[Queue] = None
    exchange: Optional[Exchange] = None


class OperationBinding(BaseModel):
    """A class to represent an operation binding.

    Attributes:
        cc : optional string representing the cc
        ack : boolean indicating if the operation is acknowledged
        replyTo : optional dictionary representing the replyTo
        bindingVersion : string representing the binding version
    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """

    cc: Optional[str] = None
    ack: bool = True
    replyTo: Optional[Dict[str, Any]] = None
    bindingVersion: str = "0.2.0"