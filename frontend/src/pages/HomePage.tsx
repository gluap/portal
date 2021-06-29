import React from 'react'
import {Link} from 'react-router-dom'
import {Message, Grid, Loader, Header, Item} from 'semantic-ui-react'
import {useObservable} from 'rxjs-hooks'
import {of, from} from 'rxjs'
import {map, switchMap} from 'rxjs/operators'
import {fromLonLat} from 'ol/proj'

import api from 'api'
import {Stats, Map, Page, RoadsLayer} from 'components'

import {TrackListItem} from './TracksPage'
import styles from './HomePage.module.scss'

function WelcomeMap() {
  return (
    <Map className={styles.welcomeMap}>
      <RoadsLayer />
      <Map.TileLayer
        osm={{
          url: 'https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png',
          crossOrigin: null,
        }}
      />
      {/* <Map.View maxZoom={22} zoom={6} center={fromLonLat([10, 51])} /> */}
      <Map.View maxZoom={22} zoom={13} center={fromLonLat([8.653950491088523,49.87128069498298])} />
    </Map>
  )
}


function MostRecentTrack() {
  const track: Track | null = useObservable(
    () =>
      of(null).pipe(
        switchMap(() => from(api.fetch('/tracks?limit=1'))),
        map((response) => response?.tracks?.[0])
      ),
    null,
    []
  )

  return (
    <>
      <Header as="h2">Most recent track</Header>
      <Loader active={track === null} />
      {track === undefined ? (
        <Message>
          No public tracks yet. <Link to="/upload">Upload the first!</Link>
        </Message>
      ) : track ? (
        <Item.Group>
          <TrackListItem track={track} />
        </Item.Group>
      ) : null}
    </>
  )
}

export default function HomePage() {
  return (
    <Page>
      <Grid stackable>
        <Grid.Row>
          <Grid.Column width={10}>
            <WelcomeMap />
          </Grid.Column>
          <Grid.Column width={6}>
            <Stats />
            <MostRecentTrack />
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Page>
  )
}
