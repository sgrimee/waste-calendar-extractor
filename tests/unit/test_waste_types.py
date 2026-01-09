"""Unit tests for waste_types module."""

import pytest

from waste_cal.waste_types import Languages, WasteType


class TestWasteTypeDescription:
    """Test WasteType.description() method."""

    @pytest.mark.parametrize(
        "waste_type,language,expected",
        [
            # RESIDUAL
            (WasteType.RESIDUAL, Languages.LU, "Reschtoffäll"),
            (WasteType.RESIDUAL, Languages.FR, "Déchets ménagers"),
            (WasteType.RESIDUAL, Languages.EN, "Residual waste"),
            # ORGANIC
            (WasteType.ORGANIC, Languages.LU, "Organesch Ressourcen"),
            (WasteType.ORGANIC, Languages.FR, "Déchets organiques"),
            (WasteType.ORGANIC, Languages.EN, "Organic waste"),
            # PAPER
            (WasteType.PAPER, Languages.LU, "Pabeier a Kartong"),
            (WasteType.PAPER, Languages.FR, "Papier et carton"),
            (WasteType.PAPER, Languages.EN, "Paper and cardboard"),
            # PACKAGING
            (WasteType.PACKAGING, Languages.LU, "Verpackungen"),
            (WasteType.PACKAGING, Languages.FR, "Emballages"),
            (WasteType.PACKAGING, Languages.EN, "Packaging"),
            # GLASS
            (WasteType.GLASS, Languages.LU, "Glas"),
            (WasteType.GLASS, Languages.FR, "Verre"),
            (WasteType.GLASS, Languages.EN, "Glass"),
            # ELECTRIC
            (WasteType.ELECTRIC, Languages.LU, "Elektro- an Elektronikapparater"),
            (WasteType.ELECTRIC, Languages.FR, "Appareils électriques"),
            (WasteType.ELECTRIC, Languages.EN, "Electric appliances"),
            # HEDGE
            (WasteType.HEDGE, Languages.LU, "Gréngschtëtsammlung"),
            (WasteType.HEDGE, Languages.FR, "Déchets verts"),
            (WasteType.HEDGE, Languages.EN, "Green waste"),
            # PROBLEMATIC
            (WasteType.PROBLEMATIC, Languages.LU, "Problemoffäll"),
            (WasteType.PROBLEMATIC, Languages.FR, "Déchets problématiques"),
            (WasteType.PROBLEMATIC, Languages.EN, "Problematic waste"),
            # BULKY
            (WasteType.BULKY, Languages.LU, "Sperrmüll"),
            (WasteType.BULKY, Languages.FR, "Encombrants"),
            (WasteType.BULKY, Languages.EN, "Bulky waste"),
            # CLOTHERS
            (WasteType.CLOTHERS, Languages.LU, "Aalt Gezei"),
            (WasteType.CLOTHERS, Languages.FR, "Vieux vêtements"),
            (WasteType.CLOTHERS, Languages.EN, "Old clothes"),
            # CHRISTMAS_TREES
            (WasteType.CHRISTMAS_TREES, Languages.LU, "Beemercher"),
            (WasteType.CHRISTMAS_TREES, Languages.FR, "Sapins de Noël"),
            (WasteType.CHRISTMAS_TREES, Languages.EN, "Christmas trees"),
        ],
    )
    def test_description_returns_correct_translation(self, waste_type: WasteType, language: Languages, expected: str):
        """Test that description returns correct translation for each waste type and language."""
        result = waste_type.description(language)
        assert result == expected

    def test_description_covers_all_waste_types(self):
        """Test that description method handles all waste types."""
        for waste_type in WasteType:
            for language in Languages:
                # Should not raise an exception and should return a non-empty string
                result = waste_type.description(language)
                assert isinstance(result, str)
                assert len(result) > 0


class TestWasteTypeIcon:
    """Test WasteType.icon() method."""

    @pytest.mark.parametrize(
        "waste_type,expected_icon",
        [
            (WasteType.RESIDUAL, "🗑️"),
            (WasteType.PAPER, "📦"),
            (WasteType.GLASS, "🍾"),
            (WasteType.PACKAGING, "♻️"),
            (WasteType.ORGANIC, "🍌"),
            (WasteType.CLOTHERS, "👕"),
            (WasteType.CHRISTMAS_TREES, "🎄"),
            (WasteType.HEDGE, "🌿"),
            (WasteType.PROBLEMATIC, "☢️"),
            (WasteType.ELECTRIC, "⚡"),
            (WasteType.BULKY, "🪑"),
        ],
    )
    def test_icon_returns_correct_emoji(self, waste_type: WasteType, expected_icon: str):
        """Test that icon returns correct emoji for each waste type."""
        result = waste_type.icon()
        assert result == expected_icon

    def test_icon_covers_all_waste_types(self):
        """Test that icon method handles all waste types."""
        for waste_type in WasteType:
            # Should not raise an exception and should return a non-empty string
            result = waste_type.icon()
            assert isinstance(result, str)
            assert len(result) > 0

    def test_icon_returns_emoji_characters(self):
        """Test that all icons are actual emoji characters."""
        for waste_type in WasteType:
            icon = waste_type.icon()
            # All our icons should be emoji characters (they have Unicode category So or Sm)
            # For simplicity, we'll just check they're not alphanumeric
            assert not icon.isalnum()
            assert len(icon) >= 1  # Emojis can be multi-byte but should have length >= 1


class TestLanguagesEnum:
    """Test Languages enum."""

    def test_languages_enum_values(self):
        """Test that Languages enum has expected values."""
        assert Languages.LU.value == "Luxembourgish"
        assert Languages.FR.value == "French"
        assert Languages.EN.value == "English"

    def test_languages_enum_completeness(self):
        """Test that we have exactly the expected languages."""
        expected_languages = {"LU", "FR", "EN"}
        actual_languages = {lang.name for lang in Languages}
        assert actual_languages == expected_languages


class TestWasteTypeEnum:
    """Test WasteType enum."""

    def test_waste_type_enum_values(self):
        """Test that WasteType enum has expected values."""
        expected_waste_types = {
            "RESIDUAL": "residual",
            "ORGANIC": "organic",
            "PAPER": "paper",
            "PACKAGING": "packaging",
            "GLASS": "glass",
            "ELECTRIC": "electric",
            "HEDGE": "hedge",
            "PROBLEMATIC": "problematic",
            "BULKY": "bulky",
            "CLOTHERS": "clothers",
            "CHRISTMAS_TREES": "christmas_trees",
        }

        for name, value in expected_waste_types.items():
            waste_type = getattr(WasteType, name)
            assert waste_type.value == value

    def test_waste_type_enum_completeness(self):
        """Test that we have exactly the expected waste types."""
        expected_count = 17  # 11 original + 6 new CSV types
        actual_count = len(list(WasteType))
        assert actual_count == expected_count


class TestWasteTypeAlarms:
    """Test WasteType alarm functionality."""

    @pytest.mark.parametrize(
        "waste_type,should_have_alarm",
        [
            # Regular collection types should have alarms
            (WasteType.RESIDUAL, True),
            (WasteType.ORGANIC, True),
            (WasteType.PAPER, True),
            (WasteType.PACKAGING, True),
            (WasteType.GLASS, True),
            # Special collection types should not have alarms
            (WasteType.ELECTRIC, False),
            (WasteType.HEDGE, False),
            (WasteType.PROBLEMATIC, False),
            (WasteType.BULKY, False),
            (WasteType.CLOTHERS, False),
            (WasteType.CHRISTMAS_TREES, False),
        ],
    )
    def test_has_alarm_returns_correct_value(self, waste_type: WasteType, should_have_alarm: bool):
        """Test that has_alarm returns correct value for each waste type."""
        result = waste_type.has_alarm()
        assert result == should_have_alarm

    @pytest.mark.parametrize(
        "waste_type,language,expected_contains",
        [
            # RESIDUAL
            (WasteType.RESIDUAL, Languages.LU, ["Moien!", "Denkt drun:", "Reschtoffäll", "muer ofgeholl"]),
            (WasteType.RESIDUAL, Languages.FR, ["Rappel:", "Déchets ménagers", "collecté demain"]),
            (WasteType.RESIDUAL, Languages.EN, ["Reminder:", "Residual waste", "collected tomorrow"]),
            # ORGANIC
            (WasteType.ORGANIC, Languages.LU, ["Moien!", "Denkt drun:", "Organesch Ressourcen", "muer ofgeholl"]),
            (WasteType.ORGANIC, Languages.FR, ["Rappel:", "Déchets organiques", "collecté demain"]),
            (WasteType.ORGANIC, Languages.EN, ["Reminder:", "Organic waste", "collected tomorrow"]),
            # PAPER
            (WasteType.PAPER, Languages.LU, ["Moien!", "Denkt drun:", "Pabeier a Kartong", "muer ofgeholl"]),
            (WasteType.PAPER, Languages.FR, ["Rappel:", "Papier et carton", "collecté demain"]),
            (WasteType.PAPER, Languages.EN, ["Reminder:", "Paper and cardboard", "collected tomorrow"]),
        ],
    )
    def test_alarm_message_contains_expected_elements(
        self, waste_type: WasteType, language: Languages, expected_contains: list[str]
    ):
        """Test that alarm message contains expected elements for each language."""
        result = waste_type.alarm_message(language)
        for expected_element in expected_contains:
            assert expected_element in result

    def test_alarm_message_covers_all_languages(self):
        """Test that alarm_message method handles all languages for alarm-enabled waste types."""
        alarm_enabled_types = [wt for wt in WasteType if wt.has_alarm()]

        for waste_type in alarm_enabled_types:
            for language in Languages:
                # Should not raise an exception and should return a non-empty string
                result = waste_type.alarm_message(language)
                assert isinstance(result, str)
                assert len(result) > 0
                # Should contain the waste type description
                assert waste_type.description(language) in result
