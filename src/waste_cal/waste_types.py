from enum import Enum


class Languages(Enum):
    LU = "Luxembourgish"
    FR = "French"
    EN = "English"


class AdysEventType(Enum):
    """Event type for ADYS bin cleaning services."""

    BIN_CLEANING = "bin_cleaning"

    def description(self, language: Languages) -> str:
        """Get event description in specified language."""
        match self:
            case AdysEventType.BIN_CLEANING:
                match language:
                    case Languages.LU:
                        return "Poubelle botzen"
                    case Languages.FR:
                        return "Nettoyage poubelle organique"
                    case Languages.EN:
                        return "Organic bin cleaning"

    def icon(self) -> str:
        """Get Unicode icon for this event type."""
        match self:
            case AdysEventType.BIN_CLEANING:
                return "🚿"

    def alarm_message(self, language: Languages) -> str:
        """Get alarm message for this event type in specified language."""
        description = self.description(language)

        match language:
            case Languages.LU:
                return f"Moien! Denkt drun: {description} gëtt muer duerchgefouert."
            case Languages.FR:
                return f"Rappel: {description} sera effectué demain."
            case Languages.EN:
                return f"Reminder: {description} will be performed tomorrow."


class WasteType(Enum):
    RESIDUAL = "residual"
    ORGANIC = "organic"
    PAPER = "paper"
    PACKAGING = "packaging"
    GLASS = "glass"
    ELECTRIC = "electric"
    HEDGE = "hedge"
    PROBLEMATIC = "problematic"
    BULKY = "bulky"
    CLOTHERS = "clothers"
    CHRISTMAS_TREES = "christmas_trees"

    def description(self, language: Languages) -> str:
        """Get waste type description in specified language."""
        match self:
            case WasteType.RESIDUAL:
                match language:
                    case Languages.LU:
                        return "Reschtoffäll"
                    case Languages.FR:
                        return "Déchets ménagers"
                    case Languages.EN:
                        return "Residual waste"
            case WasteType.ORGANIC:
                match language:
                    case Languages.LU:
                        return "Organesch Ressourcen"
                    case Languages.FR:
                        return "Déchets organiques"
                    case Languages.EN:
                        return "Organic waste"
            case WasteType.PAPER:
                match language:
                    case Languages.LU:
                        return "Pabeier a Kartong"
                    case Languages.FR:
                        return "Papier et carton"
                    case Languages.EN:
                        return "Paper and cardboard"
            case WasteType.PACKAGING:
                match language:
                    case Languages.LU:
                        return "Verpackungen"
                    case Languages.FR:
                        return "Emballages"
                    case Languages.EN:
                        return "Packaging"
            case WasteType.GLASS:
                match language:
                    case Languages.LU:
                        return "Glas"
                    case Languages.FR:
                        return "Verre"
                    case Languages.EN:
                        return "Glass"
            case WasteType.ELECTRIC:
                match language:
                    case Languages.LU:
                        return "Elektro- an Elektronikapparater"
                    case Languages.FR:
                        return "Appareils électriques"
                    case Languages.EN:
                        return "Electric appliances"
            case WasteType.HEDGE:
                match language:
                    case Languages.LU:
                        return "Gréngschtëtsammlung"
                    case Languages.FR:
                        return "Déchets verts"
                    case Languages.EN:
                        return "Green waste"
            case WasteType.PROBLEMATIC:
                match language:
                    case Languages.LU:
                        return "Problemoffäll"
                    case Languages.FR:
                        return "Déchets problématiques"
                    case Languages.EN:
                        return "Problematic waste"
            case WasteType.BULKY:
                match language:
                    case Languages.LU:
                        return "Sperrmüll"
                    case Languages.FR:
                        return "Encombrants"
                    case Languages.EN:
                        return "Bulky waste"
            case WasteType.CLOTHERS:
                match language:
                    case Languages.LU:
                        return "Aalt Gezei"
                    case Languages.FR:
                        return "Vieux vêtements"
                    case Languages.EN:
                        return "Old clothes"
            case WasteType.CHRISTMAS_TREES:
                match language:
                    case Languages.LU:
                        return "Beemercher"
                    case Languages.FR:
                        return "Sapins de Noël"
                    case Languages.EN:
                        return "Christmas trees"

    def icon(self) -> str:
        """Get Unicode icon for this waste type."""
        match self:
            case WasteType.RESIDUAL:
                return "🗑️"
            case WasteType.PAPER:
                return "📦"
            case WasteType.GLASS:
                return "🍾"
            case WasteType.PACKAGING:
                return "♻️"
            case WasteType.ORGANIC:
                return "🍌"
            case WasteType.CLOTHERS:
                return "👕"
            case WasteType.CHRISTMAS_TREES:
                return "🎄"
            case WasteType.HEDGE:
                return "🌿"
            case WasteType.PROBLEMATIC:
                return "☢️"
            case WasteType.ELECTRIC:
                return "⚡"
            case WasteType.BULKY:
                return "🪑"

    def has_alarm(self) -> bool:
        """Check if this waste type should have reminder alarms."""
        regular_collection_types = {
            WasteType.RESIDUAL,
            WasteType.ORGANIC,
            WasteType.PAPER,
            WasteType.PACKAGING,
            WasteType.GLASS,
        }
        return self in regular_collection_types

    def alarm_message(self, language: Languages) -> str:
        """Get alarm message for this waste type in specified language."""
        waste_description = self.description(language)

        match language:
            case Languages.LU:
                return f"Moien! Denkt drun: {waste_description} gëtt muer ofgeholl."
            case Languages.FR:
                return f"Rappel: {waste_description} sera collecté demain."
            case Languages.EN:
                return f"Reminder: {waste_description} will be collected tomorrow."
