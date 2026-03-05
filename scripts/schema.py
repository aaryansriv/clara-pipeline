"""
Clara Pipeline — Data Models
Defines structured schema for Account Memo, Agent Spec, and helper types.
"""

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


@dataclass
class BusinessHours:
    days: List[str] = field(default_factory=list)
    start: Optional[str] = None
    end: Optional[str] = None
    timezone: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "BusinessHours":
        if data is None:
            return cls()
        return cls(
            days=data.get("days") or [],
            start=data.get("start"),
            end=data.get("end"),
            timezone=data.get("timezone"),
        )


@dataclass
class RoutingRule:
    name: Optional[str] = None
    phone: Optional[str] = None
    order: int = 1
    fallback: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RoutingRule":
        return cls(
            name=data.get("name"),
            phone=data.get("phone"),
            order=data.get("order", 1),
            fallback=data.get("fallback"),
        )


@dataclass
class CallTransferRules:
    timeout_seconds: Optional[int] = None
    retries: Optional[int] = None
    message_if_fails: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CallTransferRules":
        if data is None:
            return cls()
        return cls(
            timeout_seconds=data.get("timeout_seconds"),
            retries=data.get("retries"),
            message_if_fails=data.get("message_if_fails"),
        )


@dataclass
class PricingInfo:
    service_call_fee: Optional[str] = None
    hourly_rate: Optional[str] = None
    billing_increment: Optional[str] = None
    disclose_on_request_only: bool = False
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "PricingInfo":
        if data is None:
            return cls()
        return cls(
            service_call_fee=data.get("service_call_fee"),
            hourly_rate=data.get("hourly_rate"),
            billing_increment=data.get("billing_increment"),
            disclose_on_request_only=data.get("disclose_on_request_only", False),
            notes=data.get("notes"),
        )


@dataclass
class NotificationChannels:
    email: Optional[str] = None
    sms: Optional[str] = None
    webhook: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "NotificationChannels":
        if data is None:
            return cls()
        return cls(
            email=data.get("email"),
            sms=data.get("sms"),
            webhook=data.get("webhook"),
        )


@dataclass
class AccountMemo:
    account_id: str = ""
    company_name: str = ""
    owner_name: Optional[str] = None
    business_hours: Optional[BusinessHours] = None
    office_address: Optional[str] = None
    services_supported: List[str] = field(default_factory=list)
    emergency_definition: List[str] = field(default_factory=list)
    emergency_routing_rules: List[RoutingRule] = field(default_factory=list)
    non_emergency_routing_rules: Optional[str] = None
    call_transfer_rules: Optional[CallTransferRules] = None
    integration_constraints: List[str] = field(default_factory=list)
    after_hours_flow_summary: Optional[str] = None
    office_hours_flow_summary: Optional[str] = None
    pricing_info: Optional[PricingInfo] = None
    notification_channels: Optional[NotificationChannels] = None
    questions_or_unknowns: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    version: str = "v1"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        d = {
            "account_id": self.account_id,
            "company_name": self.company_name,
            "owner_name": self.owner_name,
            "business_hours": self.business_hours.to_dict() if self.business_hours else None,
            "office_address": self.office_address,
            "services_supported": self.services_supported,
            "emergency_definition": self.emergency_definition,
            "emergency_routing_rules": [r.to_dict() for r in self.emergency_routing_rules],
            "non_emergency_routing_rules": self.non_emergency_routing_rules,
            "call_transfer_rules": self.call_transfer_rules.to_dict() if self.call_transfer_rules else None,
            "integration_constraints": self.integration_constraints,
            "after_hours_flow_summary": self.after_hours_flow_summary,
            "office_hours_flow_summary": self.office_hours_flow_summary,
            "pricing_info": self.pricing_info.to_dict() if self.pricing_info else None,
            "notification_channels": self.notification_channels.to_dict() if self.notification_channels else None,
            "questions_or_unknowns": self.questions_or_unknowns,
            "notes": self.notes,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "AccountMemo":
        bh = data.get("business_hours")
        routing = data.get("emergency_routing_rules") or []
        ct = data.get("call_transfer_rules")
        pi = data.get("pricing_info")
        nc = data.get("notification_channels")

        return cls(
            account_id=data.get("account_id", ""),
            company_name=data.get("company_name", ""),
            owner_name=data.get("owner_name"),
            business_hours=BusinessHours.from_dict(bh) if bh else None,
            office_address=data.get("office_address"),
            services_supported=data.get("services_supported") or [],
            emergency_definition=data.get("emergency_definition") or [],
            emergency_routing_rules=[RoutingRule.from_dict(r) for r in routing],
            non_emergency_routing_rules=data.get("non_emergency_routing_rules"),
            call_transfer_rules=CallTransferRules.from_dict(ct) if ct else None,
            integration_constraints=data.get("integration_constraints") or [],
            after_hours_flow_summary=data.get("after_hours_flow_summary"),
            office_hours_flow_summary=data.get("office_hours_flow_summary"),
            pricing_info=PricingInfo.from_dict(pi) if pi else None,
            notification_channels=NotificationChannels.from_dict(nc) if nc else None,
            questions_or_unknowns=data.get("questions_or_unknowns") or [],
            notes=data.get("notes"),
            version=data.get("version", "v1"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "AccountMemo":
        return cls.from_dict(json.loads(json_str))


@dataclass
class AgentSpec:
    account_id: str = ""
    agent_name: str = ""
    version: str = "v1"
    voice_style: str = "professional-female-warm"
    system_prompt: str = ""
    key_variables: Dict[str, Any] = field(default_factory=dict)
    tool_invocation_placeholders: List[str] = field(default_factory=list)
    call_transfer_protocol: str = ""
    fallback_protocol: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "account_id": self.account_id,
            "agent_name": self.agent_name,
            "version": self.version,
            "voice_style": self.voice_style,
            "system_prompt": self.system_prompt,
            "key_variables": self.key_variables,
            "tool_invocation_placeholders": self.tool_invocation_placeholders,
            "call_transfer_protocol": self.call_transfer_protocol,
            "fallback_protocol": self.fallback_protocol,
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "AgentSpec":
        return cls(
            account_id=data.get("account_id", ""),
            agent_name=data.get("agent_name", ""),
            version=data.get("version", "v1"),
            voice_style=data.get("voice_style", "professional-female-warm"),
            system_prompt=data.get("system_prompt", ""),
            key_variables=data.get("key_variables", {}),
            tool_invocation_placeholders=data.get("tool_invocation_placeholders", []),
            call_transfer_protocol=data.get("call_transfer_protocol", ""),
            fallback_protocol=data.get("fallback_protocol", ""),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
        )
