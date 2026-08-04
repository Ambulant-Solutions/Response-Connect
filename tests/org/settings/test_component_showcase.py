def test_component_showcase_renders(
    authenticated_org_client,
) -> None:
    response = authenticated_org_client.get(
        "/org/settings/dev/components"
    )

    assert response.status_code == 200
    assert b"Administration UI components" in response.data
    assert b"Journal timeline" in response.data
    assert b"Operations Control" in response.data