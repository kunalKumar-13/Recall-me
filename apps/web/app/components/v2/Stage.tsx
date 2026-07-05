/**
 * The workspace stage — a fixed 960×540 canvas the film engine
 * drives. Pure markup; every dynamic element carries a data attribute
 * the engine queries inside its own container, so multiple stages
 * could coexist.
 */
export function Stage() {
  return (
    <div data-stagebox className="stagebox">
      <div data-stage className="stage" aria-label="Recall product demo">
        <div className="mbar">
          <span className="msq" />
          <span>recall — demo workspace</span>
          <span className="mck" data-mclock>
            9:41 AM
          </span>
        </div>
        <div className="fwin winEd">
          <div className="tb">
            <span className="td" />
            <span className="td" />
            socket.rs — ~/dev/relay
          </div>
          <div className="codebox">
            <span data-edcode />
            <span className="ecaret" data-edcaret />
          </div>
        </div>
        <div className="fwin winBr">
          <div className="tb">
            <span className="td" />
            <span className="td" />
            browser
          </div>
          <div className="brTabs" data-brtabs />
          <div className="brPage" data-brpage />
        </div>
        <div className="fwin winCh">
          <div className="tb">
            <span className="td" />
            <span className="td" />
            chatgpt.com
          </div>
          <div className="chbody">
            <div className="bub user" data-bubq>
              <span data-chq />
            </div>
            <div className="bub" data-buba>
              <span data-cha />
            </div>
          </div>
        </div>
        <div className="notif" data-notif>
          <div className="nt">Calendar</div>
          <div className="nb">Standup — now</div>
        </div>
        <div className="tcard" data-tcard>
          <div>
            <em>Six hours later.</em>
          </div>
        </div>
        <div className="keys" data-keys>
          <span className="kcap" data-kctrl>
            ⌃
          </span>
          <span className="plus">+</span>
          <span className="kcap" data-kspace>
            space
          </span>
        </div>
        <div className="keyEnter" data-keyenter>
          <span className="kcap" data-kret>
            ↵
          </span>
        </div>
        <div className="rpanel" data-rpanel>
          <div className="rp-h">Continue where you left off</div>
          <div className="rp-row">
            <div>
              <div className="rp-t">WebSocket reconnect bug</div>
              <div className="rp-c">
                1 file · 1 chat · 2 tabs · left mid-implementation
              </div>
            </div>
            <span className="rp-hint">↵ resume</span>
          </div>
          <div className="rp-f">
            <span>↑↓ move</span>
            <span>↵ resume</span>
            <span>esc close</span>
          </div>
        </div>
        <span className="olabel lb1" data-lb1>
          1 · files
        </span>
        <span className="olabel lb2" data-lb2>
          2 · chats
        </span>
        <span className="olabel lb3" data-lb3>
          3 · tabs
        </span>
        <div className="toast" data-toast>
          Restored — 1 file · 1 chat · 2 tabs
        </div>
        <div className="endcard" data-endcard>
          <div>
            Never lose
            <br />
            the thread.
          </div>
        </div>
        <div className="chip">
          <i />
          recall — capturing
        </div>
        <div data-flies />
      </div>
    </div>
  );
}
